#!/bin/bash
#
# this script will start the xml validator server
#
# Lavaux Gilles 07/2014
#

# unset the DISPLAY, because we dont want that ssh or other things 'lock' the display and avoid exiting the shell if some processes runs.
# also because DISPLAY is not needed/wanted. See GL for more info
unset DISPLAY


#
PWD=`pwd`
cd `dirname $0`
soft_PATH=`pwd`
libs_PATH="${soft_PATH}/libs"
echo "soft_PATH=${soft_PATH}"
echo "libs_PATH=${libs_PATH}"

. ${soft_PATH}/env

SRV_NAME="xmlValidator"

# java
echo ""
echo "using java:"
java -version

#
CLASSPATH="${soft_PATH}"
(for jar in `ls ${libs_PATH}/*.jar`
do
        CLASSPATH=$jar:$CLASSPATH
done)>/dev/null 2>&1

echo ""
echo ""
echo "using CLASSPATH=$CLASSPATH"
echo "using PATH=$PATH"

if [ $# -gt 0 ];then
	echo "syntax run_xmlValidatorServer.sh"
	exit
fi

echo ""
echo "starting..."


echo "COMMAND:java -Dlog4j.debug=true -cp ${CLASSPATH} -jar serviceServer/webServer-with-handlers.jar ${CONFIGURATION_xmlValidator}"
java -Dlog4j.debug=true -cp ${CLASSPATH} -jar serviceServer/webServer-with-handlers.jar ${CONFIGURATION_xmlValidator}


cd $PWD
