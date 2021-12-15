import bot


def isCorrectNameTest(name):
    name = "Сергеевский Максим Дмитриевич"
    assert bot.isCorrectName(name)
