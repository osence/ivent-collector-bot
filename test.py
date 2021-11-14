def getAllIvents():
    # code
    return list(list(id, name))  # sort by ascending date


def searchLocation(coords):
    # code
    return list(list(id, name))  # sort by ascending date


def searchDate(dateStart, dateEnd):
    # code
    return list(list(id, name))  # sort by ascending date


def searchThematic(thema):
    # code
    return list(list(id, name))  # sort by ascending date


def searchPay(minCost, maxCost):
    # code
    return list(list(id, name))  # sort by ascending date


def userRegistration(id, fio, dataBirthday):
    # code
    return bool  # True or False (result of inserting in DB)


def userEditInfo(id, fio, dataBirthday):
    # code
    return bool  # True or False (result of inserting in DB)  


def userGetInfo(id):
    # code
    return list(fio, dataBirthday)


def newIvent(iventId, iventName, description, date, time, place, subject, payMode, numberOfSeats, userId):
    # code
    return bool  # True or False (result of inserting in DB) 


def editIventInfo(iventId, iventName, description, date, time, place, subject, payMode, numberOfSeats, userId):
    # code
    return bool  # True or False (result of inserting in DB) 


def removeIvent(iventId):
    # code
    return bool  # True or False (result of inserting in DB) 


def getIventInfo(iventId):
    # code
    return list(iventId, iventName, description, date, time, place, subject, payMode, numberOfSeats, userId)


def userAddIventRegistration(userId, iventId):
    # code
    return bool  # True or False (result of inserting in DB) 


def userRemoveIventRegistration(userId, iventId):
    # code
    return bool  # True or False (result of inserting in DB) 


def userGetIventRegistrations(userId):
    # code
    return list(iventId, iventName)  # sort by ascending date


def showIventsAddedByUser(userId):
    # code
    return list(iventId, iventName)  # sort by ascending date


def getMapFromCoords(coords):
    # code
    return link  # link to map


def getMapFromAdress(adress):
    # code
    return link  # link to map    


def handler(userRequest):
    if (userRequest == 'getAllIvents'):
        getAllIvents()
    elif (userRequest == 'searchLocation')
        searchLocation()
        # ...
    return bool  # True or False (return of the called function)

def requestSender(request):
    answer = sendToBD(request)
    return answer   # list from database