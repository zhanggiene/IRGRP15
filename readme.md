
<https://www.youtube.com/watch?v=5gPhZm9XzAY&list=PL6YwPExkSESo9FfA2msf2Wi9FC-0-JQRz&index=5> 
<https://www.youtube.com/watch?v=rxoS1p1TaFY&t=4s> 
/usr/local/var/lib/solr/test2 

1. JAVA JRE
install java 19 
```
➜  InformationRetrival java -version
java version "19.0.2" 2023-01-17
Java(TM) SE Runtime Environment (build 19.0.2+7-44)
Java HotSpot(TM) 64-Bit Server VM (build 19.0.2+7-44, mixed mode, sharing)
```
brew install solr

go to admin page <http://localhost:8983/solr/> 
solr start 
solr stop -p 8983


define index
create a core: 
solr create -c test2


add field

post -c test2 ./reviewshort.csv
