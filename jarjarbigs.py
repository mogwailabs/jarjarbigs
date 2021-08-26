#!/usr/bin/env python3

import tempfile
import sys
import shutil
import os
import argparse
import zipfile
from glob import glob

from os import listdir
from os.path import isfile, join

log_entries = []

def scan_directory(directory):
	archives = [y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.jar'))]
	archives += ([y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.war'))])
	archives += ([y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.ear'))])
	return archives



def copy_class_files(archive, source, destination):
	class_files = [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*.class'))]

	if arguments.logfile:
		log_file = open(arguments.logfile[0], "a")

	for class_file in class_files:
		current_path = os.path.dirname(class_file)[len(source):]
		current_path = current_path.replace('WEB-INF/classes/', '')
		current_file = os.path.basename(class_file)
		destination_path = destination + current_path
		if not destination_path.endswith("/"):
			destination_path += "/"

		# check if the path exists, if not, create it
		if not os.path.exists(destination_path):
			os.makedirs(destination_path)

		# Copy the class file to the new destination
		shutil.copyfile(class_file, destination_path + current_file)

		# Log the file
		if arguments.logfile:
			log_file.write("{}: {}\n".format(os.path.basename(archive), current_path[1:] + current_file))
	
	if arguments.logfile:
		log_file.close()


def copy_xml_files(archive, source, destination):
	xml_files = [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*.xml'))]
	xml_files += [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*.properties'))]

	for xml_file in xml_files:
		current_path = os.path.dirname(xml_file)[len(source):]
		current_file = os.path.basename(xml_file)
		destination_path = destination + '/' + os.path.basename(archive) + current_path
		if not destination_path.endswith("/"):
			destination_path += "/"

		# check if the path exists, if not, create it
		if not os.path.exists(destination_path):
			os.makedirs(destination_path)

		# Copy the class file to the new destination
		shutil.copyfile(xml_file, destination_path + current_file)


def extract_archive(archive_file):
	print("[+] Processing " + archive_file)
	temp_dir = tempfile.mkdtemp(prefix = "jarjarbigs")

	archive = zipfile.ZipFile(archive_file, 'r')
	try:
		archive.extractall(temp_dir)
	except FileExistsError as file_exists_error:
		print("[?] Warning! The archive \"{archive_file}\" seems to have a broken file structure. Found douplicate file when trying to write to \"{error_filepath}\". Continuing anyway, result most likely incomplete (please check the contents of the affected archive).".format(archive_file=archive_file, error_filepath=str(file_exists_error.filename)))

	directories = [temp_dir]

	dir_archives = scan_directory(temp_dir)
	if len(dir_archives) != 0:

		print("[+] new archive(s) found: " + str(dir_archives))

		for new_archive in dir_archives:
			tmp_dirs = extract_archive(new_archive)
			directories += tmp_dirs

	return directories


def create_jar_archive(source_directory, archive_name):
	print("[+] Creating jar archive " + archive_name)
	shutil.make_archive(archive_name, 'zip', source_directory)
	os.rename(archive_name + ".zip", archive_name)


def create_zip_archive(source_directory, archive_name):
	print("[+] Creating zip archive " + archive_name)
	shutil.make_archive(archive_name, 'zip', source_directory)
	os.rename(archive_name + ".zip", archive_name)


if __name__ == '__main__':
	print("--- jarjarbigs.py 0.1 by MOGWAI LABS GmbH --------------------------------------\n")

	parser = argparse.ArgumentParser(description="jarjarbigs.py - create a huge jar file from existing jar/war/ear files")
	parser.add_argument('source', help="source directory with jar/war/ear files")
	parser.add_argument('destination', help="destination jar file")
	parser.add_argument('-l', '--logfile', nargs=1, default=None, help='Create a log file which jar contains which classes')
	parser.add_argument('-x', '--xml', nargs=1, default=None, help='Create a second zip archive that contains all xml- and property files')

	arguments = parser.parse_args()

	if sys.version_info[0] < 3:
		print("[-] Please use Python3 (for zip64 support)")
		exit(2)

	if not os.path.isdir(arguments.source):
		print("[-] source does not exists or is not a directory")
		exit(1)
		

	archives = scan_directory(arguments.source)
	destination_directory = tempfile.mkdtemp(prefix = "jarjarbigs")
	xml_destination_directory = tempfile.mkdtemp(prefix = "jarjarbigs")


	for archive in archives:
		directories = extract_archive(archive)

		for source_directory in directories:
			copy_class_files(archive, source_directory, destination_directory)

			if arguments.xml is not None:
				copy_xml_files(archive, source_directory, xml_destination_directory)

			shutil.rmtree(source_directory)

	create_jar_archive(destination_directory, arguments.destination)

	if arguments.xml is not None:
		create_zip_archive(xml_destination_directory, arguments.xml[0])
	shutil.rmtree(destination_directory)
	shutil.rmtree(xml_destination_directory)
