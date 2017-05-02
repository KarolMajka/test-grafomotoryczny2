#!/usr/bin/python

from struct import unpack

class Mtb(object):
    nazwaPliku = object
    data = ''
    notatki = ''
    pakietyDanych = []

    def __init__(self, nazwaPliku, data, notatki, pakietyDanych):
        self.nazwaPliku = nazwaPliku
        self.data = data
        self.notatki = notatki
        #pakietyDanych.sort(key=lambda x: x.momentPomiaru, reverse=False)
        self.pakietyDanych = sorted(pakietyDanych, key=lambda x: x.momentPomiaru, reverse=False)



class PakietDanych(object):
    momentPomiaru = 0.0
    polozenieX = 0.0
    polozenieY = 0.0
    nacisk = 0.0
    szerokoscKatowa = 0.0
    wysokoscKatowa = 0.0

    def __init__(self, momentPomiaru, polozenieX, polozenieY, nacisk, szerokoscKatowa, wysokoscKatowa):
        self.momentPomiaru = momentPomiaru
        self.polozenieX = polozenieX
        self.polozenieY = polozenieY
        self.nacisk = nacisk
        self.szerokoscKatowa = szerokoscKatowa
        self.wysokoscKatowa = wysokoscKatowa


class NazwaPliku(object):
    lp = ''
    idPacjenta = ''
    nrOperacji = ''
    badanie = ''
    plec = ''
    reka = ''
    polkula = ''
    zabieg = ''

    def __init__(self, lp, idPacjenta, nrOperacji, badanie, plec, reka, polkula, zabieg):
        self.lp = lp
        self.idPacjenta = idPacjenta
        self.nrOperacji = nrOperacji
        self.badanie = badanie
        self.plec = plec
        self.reka = reka
        self.polkula = polkula
        self.zabieg = zabieg

    def toString(self):
        return self.lp + '_' + self.idPacjenta + '_' + \
               self.nrOperacji + self.badanie + self.plec + self.reka + self.polkula + self.zabieg

#----------------------------------------------------------------------------------------



def loadMtbFileStructure(fileName):
    f = open(fileName, "rb")
    try:
        fileNameLenghtBytes = f.read(4)
        fileNameLenghtNode = unpack('i', fileNameLenghtBytes)
        fileNameLenght = sum(fileNameLenghtNode)
        fileName = loadFileNameStructure(f.read(fileNameLenght).decode("utf-8"))

        dateLenghtBytes = f.read(4)
        dateLenghtNode = unpack('i', dateLenghtBytes)
        dateLenght = sum(dateLenghtNode)
        date = f.read(dateLenght).decode("utf-8")

        notesLenghtBytes = f.read(4)
        notesLenghtNode = unpack('i', notesLenghtBytes)
        notesLenght = sum(notesLenghtNode)
        notes = f.read(notesLenght).decode("utf-8")
        f.read(16)

        dataPacketsLenghtBytes = f.read(4)
        dataPacketsLenghtNode = unpack('i', dataPacketsLenghtBytes)
        dataPacketsLenght = sum(dataPacketsLenghtNode)
        dataPackets = []
        for i in range(0, dataPacketsLenght):
            dataPacket = loadDataPacketStructure(f.read(24))
            dataPackets.append(dataPacket)
    finally:
        f.close()
    mtbFile = Mtb(fileName, date, notes, dataPackets)
    return mtbFile


def loadDataPacketStructure(dataPacketBytes):
    momentPomiaru = sum(unpack('i', dataPacketBytes[0:4]))
    polozenieX = sum(unpack('i', dataPacketBytes[4:8]))
    polozenieY = sum(unpack('i', dataPacketBytes[8:12]))
    nacisk = sum(unpack('i', dataPacketBytes[12:16]))
    szerokoscKatowa = sum(unpack('i', dataPacketBytes[16:20]))
    wysokoscKatowa = sum(unpack('i', dataPacketBytes[20:24]))
    return PakietDanych(momentPomiaru, polozenieX, polozenieY, nacisk, szerokoscKatowa, wysokoscKatowa)


def loadFileNameStructure(fileNameString):
    lp = fileNameString[:fileNameString.find('_', 0)]
    tmp = fileNameString.find('_', len(lp) + 1)
    idPacjenta = fileNameString[len(lp) + 1:tmp]
    nrOperacji = fileNameString[tmp + 1]
    badanie = fileNameString[tmp + 2]
    plec = fileNameString[tmp + 3]
    reka = fileNameString[tmp + 4]
    polkula = fileNameString[tmp + 5]
    zabieg = fileNameString[tmp + 6]
    return NazwaPliku(lp, idPacjenta, nrOperacji, badanie, plec, reka, polkula, zabieg)
