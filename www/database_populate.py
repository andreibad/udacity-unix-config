from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

engine = create_engine('postgres://catalog:catalog@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



category1 = Category(name="El-Aurians")
session.add(category1)
session.commit()
item2 = Item(name="Guinan", description="Guinan is one of the few survivors of her kind, the El-Aurian. Her job aboard the USS Enterprise-D is technically running the lounge area Ten Forward, but she also provides counsel for her patrons. El-Aurians were a humanoid species of \"listeners\" originating from the El-Aurian system.  ",
                      category=category1)
session.add(item2)
session.commit()


category2 = Category(name="The Borg")
session.add(category2)
session.commit()
item1 = Item(name="The Borg Queen", description="The Borg Queen is similar to the queen of an insect hive. She brings order to the drones. She's the head of one of the most feared species in the Star Trek universe. What's even scarier is her appearance, where you sometimes see her as just a head and torso!",
             category=category2)
session.add(item1)
session.commit()
item2 = Item(name="Locutus of Borg", description="During their mission to assimilate Earth, the Borg decided that a human voice was necessary to facilitate their introduction into human society. Captain Picard was chosen to be that voice. And that voice was dubbed Locutus of Borg.Despite Picard's insistence that he would resist the Borg with his last ounce of strength, that resistance proved futile and he was assimilated into the Borg Collective. He became one with the hive mind; he had the Borg's cybernetic devices implanted throughout his body. Locutus' distinctive Borg feature was a single, red-laser ocular implant.",
             category=category2)
session.add(item2)
session.commit()



category1 = Category(name="Androids")
session.add(category1)
session.commit()
item1 = Item(name="Data", description="Data is the only android in Starfleet, and as such, he is quite unique. His mental prowess is staggering because he embodies the forefront of technology. Dr. Soong created him to be the perfect android, and Data is so advanced that he's considered to be sentient, according to Captain Janeway. Data's mind, as well as his physical strength, have gotten the Enterprise-D crew out of many tough spots (not a pun about his pet cat, but we're going to leave it anyway).", 
             category=category1)
session.add(item1)
session.commit()



category1 = Category(name="Q Continuum")
session.add(category1)
session.commit()
item1 = Item(name="Q", description="The first crew to meet Q is the Enterprise-D, and Captain Picard calls him one of the most unique life forms he has encountered. Captain Janeway and the Voyager crew, as well as the Deep Space Nine crew also had the unique pleasure of meeting Q. Q is of the Q Continuum, god-like immortal beings. What they think happens. ",
             category=category1)

session.add(item1)
session.commit()



category1 = Category(name="Klingons")
session.add(category1)
session.commit()
item1 = Item(name="Worf", description="Worf - son of Mogh, of the Klingon House of Martok, of the Human family Rozhenko; mate to K'Ehleyr, father to Alexander Rozhenko, and husband to Jadzia Dax; Starfleet officer and soldier of the Empire; bane of the House of Duras; slayer of Gowron; Federation ambassador to Qo'noS - was one of the most influential Klingons of the latter half of the 24th century. ",
             category=category1)
session.add(item1)
session.commit()
item2 = Item(name="Kor", description="Dahar Master Kor, son of Rynar was a male Klingon military officer and ambassador in the 23rd and 24th centuries. He was among the most influential warriors and respected military leaders of the Klingon Empire. ", 
             category=category1)
session.add(item2)
session.commit()





print "added catalog items!"
