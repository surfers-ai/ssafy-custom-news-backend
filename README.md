# ssafy-custom-news-backend

```
python manage.py runserver
```

Hadoop과 Spark 설치

```
sudo apt-get update
sudo apt-get install default-jdk
```

poetry로 의존성 관리

Hadoop 설치 및 설정

```
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
tar -xzvf hadoop-3.4.0.tar.gz
sudo mv hadoop-3.4.0 /usr/local/hadoop
```

환경 변수 설정

```
nano ~/.bashrc
```

```
export HADOOP_HOME=/usr/local/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/bin/java
export PATH=$PATH:$JAVA_HOME/bin
```

```
source ~/.bashrc
```

Hadoop 구성 파일 수정: core-site.xml, hdfs-site.xml 등을 설정하여 단일 노드 모드로 실행되도록 구성합니다.

로컬 환경에서 Spark 사용

사이트에서 다운 받고

```
tar xvzf spark-3.5.3-bin-hadoop3.tgz
sudo mv spark-3.5.3-bin-hadoop3 /usr/local/spark
```

```
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
```

```
source ~/.bashrc
```

```
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

들어가서

```
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>

```

```
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

들어가서

```
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///home/yourusername/hadoop_data/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///home/yourusername/hadoop_data/hdfs/datanode</value>
    </property>
</configuration>
```

```
sudo apt-get install openssh-server
```

```
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

```
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/bin/java
```

```
id: travelandi01@gmail.com
pw: Ssafy10000
```
