from androguard.core.bytecodes import apk, dvm
from androguard.core.analysis.analysis import Analysis


def get_methods(vmx):
    """
    This method gives us information about a methods in an apk.
    :param vmx: androguard.core.analysis.analysis.Analysis
    :return: list of dics of methods [{"class":value,"name":value,"params":value,"return":value}]
    :rtype: list of dics
    """
    methods = []
    for vm in vmx.vms:  # todo:Test for multiple dex files in one apk?
        method = {}
        for m in vm.get_methods():
            method["class"] = dvm.get_type(m.get_class_name())  # get rid of L in start of class
            method["name"] = dvm.get_type(m.get_name())
            info = m.get_information()
            if "params" in info:
                method["params"] = []
                for param in info["params"]:
                    method["params"].append(param[1])
            if "return" in info:
                method["return"] = info["return"]
            methods.append(method)
    return methods


# Fixme: Description & action are resources, how to resolve them? https://github.com/androguard/androguard/issues/529
def get_permissions(apk):
    """
        Return permissions with details
        :rtype: list of string
    """
    permission_list = []

    # {permission: [protectionLevel, label, description]}
    # https://github.com/androguard/androguard/issues/529

    for name, detail in apk.get_details_permissions().items():
        perm = dict()
        perm["name"] = name
        perm["severity"] = detail[0]
        perm["action"] = detail[1]
        perm["description"] = detail[2]
        permission_list.append(perm)
    return permission_list


def get_extended_receivers(apk):
    """
    Return the android:name attribute of all receivers
    :rtype: a list of string
    """
    manifest = apk.xml["AndroidManifest.xml"]
    receivers = []
    application = manifest.findall("application")[0]
    for receiver in application.findall("receiver"):
        intents = receiver.findall("intent-filter")
        for intent in intents:
            actions = intent.findall("action")
            for action in actions:
                receivers.append(action.get("{http://schemas.android.com/apk/res/android}name"))
    return receivers


#TODO: To implement this function
def get_show_Permissions(dx):
    """
    Checks for functions that need permissions, more details to be added
    :param dx: Analysis object of vm
    :return: list of permissions
    :rtype: list of Strings
    """
    """
    p = dx.get_permissions( [] )
    permissions = {}
    for i in p :
        paths=[]
        #print i, ":"
        for j in p[i] :
           paths.append(get_show_Path(dx.get_vm(), j))
        permissions[i.replace("android.permission.", "").replace(".", "_")] = paths
    return permissions
    """
    return []



def search_methods(vmx, method_regex):
    """
    Looks for all occurrences in which method specified by method_regex is called. It uses Xrefs.
    :param vmx: Analysis object
    :param method_regex: String for specifying method
    :return: List of paths (caller --> callee)
    """
    list_paths = []
    for mca in vmx.find_methods(method_regex):
        for ref_class, ref_method, offset in mca.get_xref_from():
            list_paths.append("%d %s->%s%s (0x%x) ---> %s->%s%s" % (ref_method.get_access_flags(),  # Fixme
                                                        ref_method.get_class_name(),
                                                        ref_method.get_name(),
                                                        ref_method.get_descriptor(),
                                                        offset,
                                                        mca.get_method().get_class_name(),
                                                        mca.get_method().get_name(),
                                                        mca.get_method().get_descriptor()))
    return list_paths


def get_show_DynCode(vmx):
    """
        Show where dynamic code is used
        :param vmx : the analysis virtual machine
        :type vmx: a :class:`Analysis` object
        :return: List of paths (caller --> callee)
    """
    return search_methods(vmx, "Ldalvik/system/DexClassLoader;",)


def get_show_NativeMethods(vmx):
    """
        Show the native methods
        :param vmx : the analysis virtual machine
        :type vmx: a :class:`Analysis` object
    """
    native = []

    for d in vmx.vms:
        for i in d.get_methods() :
            if i.get_access_flags() & 0x100 :
                native.append( i.get_class_name()+ i.get_name()+ i.get_descriptor())
                #native.append(get_show_Path(d,i))
    return native


def get_show_ReflectionCode(vmx):
    """
        Show the reflection code
        :param vmx : the analysis virtual machine
        :type vmx: a :class:`Analysis` object
        :return: List of paths (caller --> callee)
    """
    return search_methods(vmx,"Ljava/lang/reflect/Method;", )


def get_show_CryptoCode(vmx):
    """
        Show the reflection code
        :param vmx : the analysis virtual machine
        :type vmx: a :class:`Analysis` object
        :return: List of paths (caller --> callee)
    """
    return search_methods(vmx,"Ljavax/crypto/.", )
