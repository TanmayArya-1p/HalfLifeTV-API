#Util Algos

def URL_Splitter(href):
	return (f'{href.split("/")[len(href.split("/"))-2]}/{href.split("/")[len(href.split("/"))-1]}')

def getID(href):
	return href.split("/")[len(href.split("/"))-2]

def ConvertDictValuesToInt(d:dict):
	otpt = {}
	for i in d:
		try:
			try:
				otpt[i] = int(d.get(i))
			except:
				try:
					otpt[i] = float(d.get(i))
				except:
					otpt[i] = (d.get(i))
		except:
			otpt[i] = (d.get(i))
	return otpt

def GetScore_BiggestWL(s:str):
	otpt = ""
	for i in s:
		if(i != " "):
			otpt = otpt + i
		else:
			break
	otpt = otpt.replace(":" , "-")
	return otpt

def ParseTillSpace(s:str):
	otpt = ""
	for i in s:
		if(i != " "):
			otpt = otpt + i
		else:
			break
	return otpt


import itertools

def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)
    
#Automatically creates a __repr__ method.
class AutoRepr:
	def __repr__(self):
		otpt = ""
		for i in self.__dict__:
			otpt = otpt+str(i)+"="
			if(type(self.__dict__.get(i)) == str):
				otpt=otpt+ '"'+ str(self.__dict__.get(i))+'"' + " , "
			else:
				otpt=otpt+ str(self.__dict__.get(i)) + " , "
		otpt = otpt[:-3]
		rtn = f'{self.__class__.__name__}({otpt})'
		return rtn


def Capitalize(s:str):
	otpt = s[:1].upper() + s[1:]
	return otpt


from unidecode import unidecode
def remove_non_ascii(text):
    return unidecode(unicode(text, encoding = "utf-8"))