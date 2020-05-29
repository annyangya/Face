
class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl(path):
        return path

    @staticmethod
    def buildStaticUrl(path):
        ver = "%s" % (2020)
        path = "/static" + path + "?version=" + ver
        return UrlManager.buildUrl(path)