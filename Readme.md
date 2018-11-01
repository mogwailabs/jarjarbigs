# jarjarbigs.py

JD-Eclipse (the Eclipse plugin of JD-GUI) has issues when it needs to decompile a class that is located in another archive. We can work arround this limitation by providing all class files in one big jar file.
jarjarbigs.py is a script to create such a merged jar file. It walks through the provided directory and unpacks all jar/war/ear archives (and jar/war files included in those archives). The 
.class files are then merged into one jar archive.

The generated jar file can be included as a external reference in a Eclipse project to debug a remote target via Eclipse/JD-Eclipse. 


## Usage
Using jarjarbigs.py is simple, just provide the directory with all jar/war/ear files and the name of the new jar file:

```
python3 jarjarbigs.py /opt/source/directory /home/h0ng10/work/testjar.jar
```

### Aditional options

```
-l logfile
```

Create an additional log file that logs the archive name and each extracted class file. Allows an easy search which could be useful when ceating proof of concept tools/clients.


```
-x xml-archive
```
Creates an addtional ZIP archive with all .xml and .properties files. 
