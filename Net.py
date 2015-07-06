#coding=utf-8
#!/usr/bin/python

import os
import shutil
import re

#inDir = "..\..\..\Doc\in"
#outDir = "..\..\Assets\Scripts\Network\Dispatcher"
inDir = ''
outDir = ''
inFileName = "..\..\..\Doc\Player.proto"

fileNameTemplateStructProtocol = "template\\templateStructProtocol.cs"
fileNameTemplateStruct = "template\\templateStruct.cs"
fileNameTemplateStructRW = "template\\templateStructRW.cs"
fileNameTemplateUpProtocol = "template\\templateUpProtocol.cs"
fileNameTemplateUp = "template\\templateUp.cs"
fileNameTemplateDownProtocol = "template\\templateDownProtocol.cs"
fileNameTemplateDown = "template\\templateDown.cs"
fileNameTemplateDownHandleProtocol = "template\\templateDownHandleProtocol.cs"
fileNameTemplateDownHandle = "template\\templateDownHandle.cs"
fileNameTemplateRegister = "template\\Dispatcher_Register.cs"


listModuleMethodDown = []

convertType = {'uint8':"byte",'int32':'int','uint32':'int','uint16':'short',}
#print fileName

#ParseProtocol(fileName)

def ConvertType(inType):
	if(convertType.has_key(inType)):
		return convertType[inType]
	return inType

def ParseStruct(moduleName,strStruct):
	#print strStruct
	strStruct = strStruct.expandtabs()
	strStruct = strStruct.replace("{",'')
	strStruct = strStruct.replace("}",'')
	strList = strStruct.split("\n")
	strHeader = strList[0]
	name = strHeader.split(" ")[1]
	listField = []
	for i in range(1,len(strList)):
		strField = strList[i]
		if(strField.find(";") == -1):
			continue
		strField = strField.replace(";",'')
		strListField = strField.split(" ")
		while(strListField.count('') > 0):
			strListField.remove('')
		field = {}
		field["name"] = strListField[len(strListField) - 1]
		field["type"] = strListField[len(strListField) - 2]

		field["compress"] = False
		for i in range(0,len(strListField) - 2):
			if(strListField[i] == "compress"):
				field["compress"] = True
		listField.append(field)
	struct = {'module':moduleName,"name":name,"field":listField}
	return struct

def ConvertName(name):
	#print name
	name = name.replace("ID_",'',1)
	name = name.replace("_RSP",'')
	name = name.lower()
	strList = []
	for str in name.split("_"):
		strList.append(str.capitalize())
	strJoin = ''
	name = strJoin.join(strList)
	#print name
	return name

def ParseMsg(moduleName,strMsg):
	#print strMsg
	strMsg = strMsg.expandtabs()
	strMsg = strMsg.replace("{",'')
	strMsg = strMsg.replace("}",'')
	strList = strMsg.split("\n")
	strHeader = strList[0]
	msgID = strHeader.split(" ")[1]
	name = ConvertName(msgID)
	listParam = []
	for i in range(1,len(strList)):
		strField = strList[i]
		if(strField.find(";") == -1):
			continue
		strField = strField.replace(";",'')
		strListField = strField.split(" ")
		while(strListField.count('') > 0):
			strListField.remove('')
		param = {}
		param["name"] = strListField[len(strListField) - 1]
		param["type"] = strListField[len(strListField) - 2]

		param["compress"] = False
		param["repeat"] = False
		for i in range(0,len(strListField) - 2):
			if(strListField[i] == "compress"):
				param["compress"] = True
			elif(strListField[i] == "repeat"):
				param["repeat"] = True
		listParam.append(param)
	method = {"module":moduleName,"name":name,"msgID":msgID,"param":listParam}
	return method

def GenScriptStruct(moduleName,listStruct,template,templateProtocol,templateReadWrite):
	#print listStruct
	script = template
	script = script.replace("{module}",moduleName)
	scriptDefine = ''
	scripteRW = ''
	for struct in listStruct:
		name = struct["name"]
		strListFields = []
		strListRead = []
		strListWrite = []
		fieldList = struct["field"]
		for field in fieldList:
			pName = field['name']
			pType = ConvertType(field['type'])
			pCompress = field["compress"]
			strField = "\tpublic %s %s;" % (pType,pName)
			strListFields.append(strField)

			strRead = "\t\tbs.Read(out data%s.%s);" % (name,pName)
			strListRead.append(strRead)
			strWrite = "\t\tbs.Write(data%s.%s);" % (name,pName)
			strListWrite.append(strWrite)

		strDefine = templateProtocol
		strDefine = strDefine.replace("{name}",name)
		strDefine = strDefine.replace("{msgID}",name)
		strFields = "\n"
		scriptDefine += strDefine.replace("{fields}",strFields.join(strListFields))

		strRW = templateReadWrite
		strRW= strRW.replace("{name}",name)
		strRW = strRW.replace('{read}',strFields.join(strListRead))
		strRW = strRW.replace('{write}',strFields.join(strListWrite))
		strRW = strRW.replace('{readCompressed}',strFields.join(strListRead).replace("Read","ReadCompressed"))
		strRW = strRW.replace('{writeCompressed}',strFields.join(strListWrite).replace("Write","WriteCompressed"))
		scripteRW += strRW
		
		#strMethod = strMethod.replace("{data}",strParses.join(strListParses))
		#scriptFields += strFields
	script = script.replace("{define}",scriptDefine)
	script = script.replace("{rw}",scripteRW)
	return script

def GenScriptMethodUp(moduleName,listMethod,template,templateProtocol):
	script = template
	script = script.replace("{module}",moduleName)
	scriptMethods = ''
	for method in listMethod:
		name = method["name"]
		msgID = method['msgID']
		strListParams = []
		strListParses = []
		paramList = method["param"]
		for param in paramList:
			pName = param['name']
			pType = ConvertType(param['type'])
			pCompress = param["compress"]
			pRepeat = param["repeat"]
			param = "%s %s" % (pType,pName)
			strListParams.append(param)
			writeMethod = "Write"
			if(pCompress):
				writeMethod = "WriteCompressed"
			parse = "\t\tbs.%s(%s);" % (writeMethod,pName)
			strListParses.append(parse)
		strMethod = templateProtocol
		strMethod = strMethod.replace("{name}",name)
		strMethod = strMethod.replace("{msgID}",msgID)
		strParams = ","
		strParses = "\n"
		strMethod = strMethod.replace("{param}",strParams.join(strListParams))
		strMethod = strMethod.replace("{data}",strParses.join(strListParses))
		scriptMethods += strMethod
	script = script.replace("{data}",scriptMethods)
	return script

def GenScriptMethodDown(moduleName,listMethod,template,templateProtocol):
	script = template
	script = script.replace("{module}",moduleName)
	scriptMethods = ''
	for method in listMethod:
		name = method["name"]
		msgID = method['msgID']
		strListParams = []
		strListParses = []
		paramList = method["param"]
		#print paramList
		for param in paramList:
			pName = param['name']
			pType = ConvertType(param['type'])
			pCompress = param["compress"]
			pRepeat = param["repeat"]
			if(pRepeat == True):
				param = "%sList" % (pName)
			else:
				param = "%s" % (pName)
			strListParams.append(param)
			writeMethod = "Write"
			if(pCompress):
				writeMethod = "WriteCompressed"
			if(pRepeat == True):
				parse = "\t\tList<%s> %sList;\n\t\tbs.%s(out %sList);" % (pType,pName,pCompress and 'ReadCompressed' or 'Read',pName)
			else:
				parse = "\t\t%s %s;\n\t\tbs.%s(out %s);" % (pType,pName,pCompress and 'ReadCompressed' or 'Read',pName)
			#print parse
			strListParses.append(parse)
		strMethod = templateProtocol
		strMethod = strMethod.replace("{module}",moduleName)
		strMethod = strMethod.replace("{name}",name)
		strMethod = strMethod.replace("{msgID}",msgID)
		strParams = ","
		strParses = "\n"
		strMethod = strMethod.replace("{param}",strParams.join(strListParams))
		strMethod = strMethod.replace("{data}",strParses.join(strListParses))
		scriptMethods += strMethod + "\n"
	script = script.replace("{data}",scriptMethods)
	return script

def GenScriptMethodDownHandle(moduleName,listMethod,template,templateProtocol):
	script = template
	script = script.replace("{module}",moduleName)
	scriptMethods = ''
	for method in listMethod:
		name = method["name"]
		msgID = method['msgID']
		strListParams = []
		strListParses = []
		paramList = method["param"]
		#print paramList
		for param in paramList:
			pName = param['name']
			pType = ConvertType(param['type'])
			pCompress = param["compress"]
			pRepeat = param["repeat"]
			if(pRepeat):
				param = "List<%s> %sList" % (pType,pName)
			else:
				param = "%s %s" % (pType,pName)
			strListParams.append(param)
		strMethod = templateProtocol
		strMethod = strMethod.replace("{name}",name)
		strMethod = strMethod.replace("{msgID}",msgID)
		strParams = ","
		strMethod = strMethod.replace("{param}",strParams.join(strListParams))
		scriptMethods += strMethod + "\n"
	script = script.replace("{data}",scriptMethods)
	return script

def ParseProtocolFile(fileName):
	print 'gen inFileName : ' + fileName
	fileIn = open(fileName,"r")
	fileBaseName = os.path.splitext(os.path.basename(fileIn.name))[0]
	moduleName = fileBaseName

	#print fileIn.readlines()
	fileLines = fileIn.readlines()
	fileIn.close()

	strFileList = []

	for str in fileLines:
	#print str
	#str = str.replace("\t",'')
		str = str.replace("\n",'')
		if(str.find("---") != -1 \
		or str.find("===") != -1\
		or str == ''\
		or str.find('//') == 0):
			continue
		else:
			index = str.find("//")
			if(index != -1):
				str = str[0: index - 1]
			strFileList.append(str)
	del fileLines

	#for str in strFileList:
	#	print str

	fileData = "\n".join(strFileList)
	while(fileData.find("/*") != -1 and fileData.find("*/") != -1):
		fileData = fileData.replace(fileData[fileData.find("/*"):fileData.find("*/") + 2],'')

	#fileData = fileData.replace('\\*.*/','');

	#print fileData

	listStruct = []
	#print fileData
	req = re.compile('struct[^{}]*{[^{}]*}',re.S) 
	strStructList = req.findall(fileData)
	for strStruct in strStructList:
		listStruct.append(ParseStruct(moduleName,strStruct))

	#print listStruct

	#print fileData
	listMethodUp = []
	listMethodDown = []

	req = re.compile('message[^{}]*[^{}]*{[^{}]*}',re.S) 
	strMsgList = req.findall(fileData)
	for strMsg in strMsgList:
		msg = ParseMsg(moduleName,strMsg)
		if(strMsg.find("_RSP") != -1):
			#print msg
			listModuleMethodDown.append(msg)
			listMethodDown.append(msg)
		else:
			listMethodUp.append(msg)

	fileIn = open(fileNameTemplateStructProtocol,'r')
	templateProtocolStruct = fileIn.read()
	template = open(fileNameTemplateStruct,'r').read();	
	templateStructRW = open(fileNameTemplateStructRW,'r').read();	
	script = GenScriptStruct(moduleName,listStruct,template,templateProtocolStruct,templateStructRW)
	fileOutStruct = open(outDir + '\struct\Struct' + moduleName + '.cs','w') 
	fileOutStruct.write(script)
	fileOutStruct.close()

	fileIn = open(fileNameTemplateUpProtocol,'r')
	templateProtocolUp = fileIn.read()
	template = open(fileNameTemplateUp,'r').read();	
	script = GenScriptMethodUp(moduleName,listMethodUp,template,templateProtocolUp)
	fileOutUp = open(outDir + '\up\Up' + moduleName + '.cs','w')
	fileOutUp.write(script)
	fileOutUp.close()

	fileIn = open(fileNameTemplateDownProtocol,'r')
	templateProtocolDown = fileIn.read()
	template = open(fileNameTemplateDown,'r').read();	
	script = GenScriptMethodDown(moduleName,listMethodDown,template,templateProtocolDown)
	fileOutDown = open(outDir + '\down\Down' + moduleName + '.cs','w')
	fileOutDown.write(script)
	fileOutDown.close()

	fileIn = open(fileNameTemplateDownHandleProtocol,'r')
	templateProtocolDownHandle = fileIn.read()
	template = open(fileNameTemplateDownHandle,'r').read();	
	script = GenScriptMethodDownHandle(moduleName,listMethodDown,template,templateProtocolDownHandle)
	fileOutDownHandle = open(outDir + '\handle\DownHandle' + moduleName + '.cs','w')
	fileOutDownHandle.write(script)
	fileOutDownHandle.close()

	del fileData
	return

def GenRegisterScript(methodList,template):
	script = template
	registerList = []
	for method in methodList:
		strRegister = "\t\tdispatcher.Register((byte)MsgIDTypes.{msgID}, Down{module}.OnRequest{name});"
		strRegister = strRegister.replace("{msgID}",method['msgID'])
		strRegister = strRegister.replace('{module}',method['module'])
		strRegister = strRegister.replace('{name}',method['name'])
		registerList.append(strRegister)

	strParses = "\n"
	script = script.replace("{data}",strParses.join(registerList))
	return script
#if(os.path.exists(outDir)):
#	shutil.rmtree(outDir) 

def main(inDirP,outDirP):
	global inDir
	global outDir
	inDir = inDirP
	outDir = outDirP
	#os.mkdir(outDir)
	#os.mkdir(outDir + "\up")
	#os.mkdir(outDir + "\down")
	#os.mkdir(outDir + "\handle")
	#os.mkdir(outDir + "\struct")
	
	for parent,dirNames,fileNames in os.walk(inDir):
		for fileName in fileNames:
			name,extend = os.path.splitext(fileName)
			if extend == '.proto':
				ParseProtocolFile(parent + "\\" + fileName)

	#ParseProtocolFile(inFileName);

	template = open(fileNameTemplateRegister,'r').read();	
	script = GenRegisterScript(listModuleMethodDown,template)
	fileOutRegister = open(outDir + "\Dispatcher_Register" + '.cs','w')
	fileOutRegister.write(script)
	fileOutRegister.close()