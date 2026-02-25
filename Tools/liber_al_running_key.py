"""
Liber AL vel Legis (Book of the Law) as running key for all unsolved LP pages.
Also tests against P19 known key.
"""
import os, sys
from collections import Counter

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# === GP ===
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
           'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def tokenize_english(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789&':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if i + 2 < len(text) and text[i:i+3] == 'ING':
            values.append(10); values.append(21); i += 3
        elif i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH':
                values.append(2); i += 2
            elif digraph == 'NG':
                values.append(21); i += 2
            elif digraph == 'OE':
                values.append(22); i += 2
            elif digraph == 'AE':
                values.append(25); i += 2
            elif digraph in ('IA', 'IO'):
                values.append(27); i += 2
            elif digraph == 'EA':
                values.append(28); i += 2
            elif digraph == 'EO':
                values.append(12); i += 2
            elif text[i] in ENG2GP:
                values.append(ENG2GP[text[i]]); i += 1
            else:
                i += 1
        elif text[i] in ENG2GP:
            values.append(ENG2GP[text[i]]); i += 1
        else:
            i += 1
    return values

def to_english(gp_values):
    return ''.join(LATIN[v] for v in gp_values)

def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

# Liber AL vel Legis - all 3 chapters concatenated
LIBER_AL = """Had The manifestation of Nuit
The unveiling of the company of heaven
Every man and every woman is a star
Every number is infinite there is no difference
Help me o warrior lord of Thebes in my unveiling before the Children of men
Be thou Hadit my secret centre my heart and my tongue
Behold it is revealed by Aiwass the minister of Hoor paar kraat
The Khabs is in the Khu not the Khu in the Khabs
Worship then the Khabs and behold my light shed over you
Let my servants be few and secret they shall rule the many and the known
These are fools that men adore both their Gods and their men are fools
Come forth o children under the stars and take your fill of love
I am above you and in you My ecstasy is in yours My joy is to see your joy
Above the gemmed azure is The naked splendour of Nuit She bends in ecstasy to kiss The secret ardours of Hadit The winged globe the starry blue Are mine O Ankh af na khonsu
Now ye shall know that the chosen priest and apostle of infinite space is the prince priest the Beast and in his woman called the Scarlet Woman is all power given They shall gather my children into their fold they shall bring the glory of the stars into the hearts of men
For he is ever a sun and she a moon But to him is the winged secret flame and to her the stooping starlight
But ye are not so chosen
Burn upon their brows o splendrous serpent
O azure lidded woman bend upon them
The key of the rituals is in the secret word which I have given unto him
With the God and the Adorer I am nothing they do not see me They are as upon the earth I am Heaven and there is no other God than me and my lord Hadit
Now therefore I am known to ye by my name Nuit and to him by a secret name which I will give him when at last he knoweth me Since I am Infinite Space and the Infinite Stars thereof do ye also thus Bind nothing Let there be no difference made among you between any one thing and any other thing for thereby there cometh hurt
But whoso availeth in this let him be the chief of all
I am Nuit and my word is six and fifty
Divide add multiply and understand
Then saith the prophet and slave of the beauteous one Who am I and what shall be the sign So she answered him bending down a lambent flame of blue all touching all penetrant her lovely hands upon the black earth and her lithe body arched for love and her soft feet not hurting the little flowers Thou knowest And the sign shall be my ecstasy the consciousness of the continuity of existence the omnipresence of my body
Then the priest answered and said unto the Queen of Space kissing her lovely brows and the dew of her light bathing his whole body in a sweet smelling perfume of sweat O Nuit continuous one of Heaven let it be ever thus that men speak not of Thee as One but as None and let them speak not of thee at all since thou art continuous
None breathed the light faint and faery of the stars and two
For I am divided for loves sake for the chance of union
This is the creation of the world that the pain of division is as nothing and the joy of dissolution all
For these fools of men and their woes care not thou at all They feel little what is is balanced by weak joys but ye are my chosen ones
Obey my prophet follow out the ordeals of my knowledge seek me only Then the joys of my love will redeem ye from all pain This is so I swear it by the vault of my body by my sacred heart and tongue by all I can give by all I desire of ye all
Then the priest fell into a deep trance or swoon and said unto the Queen of Heaven Write unto us the ordeals write unto us the rituals write unto us the law
But she said the ordeals I write not the rituals shall be half known and half concealed the Law is for all
This that thou writest is the threefold book of Law
My scribe Ankh af na khonsu the priest of the princes shall not in one letter change this book but lest there be folly he shall comment thereupon by the wisdom of Ra Hoor Khuit
Also the mantras and spells the obeah and the wanga the work of the wand and the work of the sword these he shall learn and teach
He must teach but he may make severe the ordeals
The word of the Law is Thelema
Who calls us Thelemites will do no wrong if he look but close into the word For there are therein Three Grades the Hermit and the Lover and the man of Earth Do what thou wilt shall be the whole of the Law
The word of Sin is Restriction O man refuse not thy wife if she will O lover if thou wilt depart There is no bond that can unite the divided but love all else is a curse Accursed Accursed be it to the aeons Hell
Let it be that state of manyhood bound and loathing So with thy all thou hast no right but to do thy will
Do that and no other shall say nay
For pure will unassuaged of purpose delivered from the lust of result is every way perfect
The Perfect and the Perfect are one Perfect and not two nay are none
Nothing is a secret key of this law Sixty one the Jews call it I call it eight eighty four hundred and eighteen
But they have the half unite by thine art so that all disappear
My prophet is a fool with his one one one are not they the Ox and none by the Book
Abrogate are all rituals all ordeals all words and signs Ra Hoor Khuit hath taken his seat in the East at the Equinox of the Gods and let Asar be with Isa who also are one But they are not of me Let Asar be the adorant Isa the sufferer Hoor in his secret name and splendour is the Lord initiating
There is a word to say about the Hierophantic task Behold there are three ordeals in one and it may be given in three ways The gross must pass through fire let the fine be tried in intellect and the lofty chosen ones in the highest Thus ye have star and star system and system let not one know well the other
There are four gates to one palace the floor of that palace is of silver and gold lapis lazuli and jasper are there and all rare scents jasmine and rose and the emblems of death Let him enter in turn or at once the four gates let him stand on the floor of the palace Will he not sink Amn Ho warrior if thy servant sink But there are means and means Be goodly therefore dress ye all in fine apparel eat rich foods and drink sweet wines and wines that foam Also take your fill and will of love as ye will when where and with whom ye will But always unto me
If this be not aright if ye confound the space marks saying They are one or saying They are many if the ritual be not ever unto me then expect the direful judgments of Ra Hoor Khuit
This shall regenerate the world the little world my sister my heart and my tongue unto whom I send this kiss Also o scribe and prophet though thou be of the princes it shall not assuage thee nor absolve thee But ecstasy be thine and joy of earth ever To me To me
Change not as much as the style of a letter for behold thou o prophet shalt not behold all these mysteries hidden therein
The child of thy bowels he shall behold them
Expect him not from the East nor from the West for from no expected house cometh that child Aum All words are sacred and all prophets true save only that they understand a little solve the first half of the equation leave the second unattacked But thou hast all in the clear light and some though not all in the dark
Invoke me under my stars Love is the law love under will Nor let the fools mistake love for there are love and love There is the dove and there is the serpent Choose ye well He my prophet hath chosen knowing the law of the fortress and the great mystery of the House of God All these old letters of my Book are aright but Tzaddi is not the Star This also is secret my prophet shall reveal it to the wise
I give unimaginable joys on earth certainty not faith while in life upon death peace unutterable rest ecstasy nor do I demand aught in sacrifice
My incense is of resinous woods and gums and there is no blood therein because of my hair the trees of Eternity
My number is eleven as all their numbers who are of us The Five Pointed Star with a Circle in the Middle and the circle is Red My colour is black to the blind but the blue and gold are seen of the seeing Also I have a secret glory for them that love me
But to love me is better than all things if under the night stars in the desert thou presently burnest mine incense before me invoking me with a pure heart and the Serpent flame therein thou shalt come a little to lie in my bosom For one kiss wilt thou then be willing to give all but whoso gives one particle of dust shall lose all in that hour Ye shall gather goods and store of women and spices ye shall wear rich jewels ye shall exceed the nations of the earth in splendour and pride but always in the love of me and so shall ye come to my joy I charge you earnestly to come before me in a single robe and covered with a rich headdress I love you I yearn to you Pale or purple veiled or voluptuous I who am all pleasure and purple and drunkenness of the innermost sense desire you Put on the wings and arouse the coiled splendour within you come unto me
At all my meetings with you shall the priestess say and her eyes shall burn with desire as she stands bare and rejoicing in my secret temple To me To me calling forth the flame of the hearts of all in her love chant
Sing the rapturous love song unto me Burn to me perfumes Wear to me jewels Drink to me for I love you I love you
I am the blue lidded daughter of Sunset I am the naked brilliance of the voluptuous night sky
To me To me
The Manifestation of Nuit is at an end
Nu the hiding of Hadit
Come all ye and learn the secret that hath not yet been revealed I Hadit am the complement of Nu my bride I am not extended and Khabs is the name of my House
In the sphere I am everywhere the centre as she the circumference is nowhere found
Yet she shall be known and I never
Behold the rituals of the old time are black Let the evil ones be cast away let the good ones be purged by the prophet Then shall this Knowledge go aright
I am the flame that burns in every heart of man and in the core of every star I am Life and the giver of Life yet therefore is the knowledge of me the knowledge of death
I am the Magician and the Exorcist I am the axle of the wheel and the cube in the circle Come unto me is a foolish word for it is I that go
Who worshipped Heru pa kraath have worshipped me ill for I am the worshipper
Remember all ye that existence is pure joy that all the sorrows are but as shadows they pass and are done but there is that which remains
O prophet thou hast ill will to learn this writing
I see thee hate the hand and the pen but I am stronger
Because of me in Thee which thou knewest not
for why Because thou wast the knower and me
Now let there be a veiling of this shrine now let the light devour men and eat them up with blindness
For I am perfect being Not and my number is nine by the fools but with the just I am eight and one in eight Which is vital for I am none indeed The Empress and the King are not of me for there is a further secret
I am The Empress and the Hierophant Thus eleven as my bride is eleven
Hear me ye people of sighing The sorrows of pain and regret Are left to the dead and the dying The folk that not know me as yet
These are dead these fellows they feel not We are not for the poor and sad the lords of the earth are our kinsfolk
Is a God to live in a dog No but the highest are of us They shall rejoice our chosen who sorroweth is not of us
Beauty and strength leaping laughter and delicious languor force and fire are of us
We have nothing with the outcast and the unfit let them die in their misery For they feel not Compassion is the vice of kings stamp down the wretched and the weak this is the law of the strong this is our law and the joy of the world Think not o king upon that lie That Thou Must Die verily thou shalt not die but live Now let it be understood If the body of the King dissolve he shall remain in pure ecstasy for ever Nuit Hadit Ra Hoor Khuit The Sun Strength and Sight Light these are for the servants of the Star and the Snake
I am the Snake that giveth Knowledge and Delight and bright glory and stir the hearts of men with drunkenness To worship me take wine and strange drugs whereof I will tell my prophet and be drunk thereof They shall not harm ye at all It is a lie this folly against self The exposure of innocence is a lie Be strong o man lust enjoy all things of sense and rapture fear not that any God shall deny thee for this
I am alone there is no God where I am
Behold these be grave mysteries for there are also of my friends who be hermits Now think not to find them in the forest or on the mountain but in beds of purple caressed by magnificent beasts of women with large limbs and fire and light in their eyes and masses of flaming hair about them there shall ye find them Ye shall see them at rule at victorious armies at all the joy and there shall be in them a joy a million times greater than this Beware lest any force another King against King Love one another with burning hearts on the low men trample in the fierce lust of your pride in the day of your wrath
Ye are against the people O my chosen
I am the secret Serpent coiled about to spring in my coiling there is joy If I lift up my head I and my Nuit are one If I droop down mine head and shoot forth venom then is rapture of the earth and I and the earth are one
There is great danger in me for who doth not understand these runes shall make a great miss He shall fall down into the pit called Because and there he shall perish with the dogs of Reason
Now a curse upon Because and his kin
May Because be accursed for ever
If Will stops and cries Why invoking Because then Will stops and does nought
If Power asks why then is Power weakness
Also reason is a lie for there is a factor infinite and unknown and all their words are skew wise
Enough of Because Be he damned for a dog
But ye o my people rise up and awake
Let the rituals be rightly performed with joy and beauty
There are rituals of the elements and feasts of the times
A feast for the first night of the Prophet and his Bride
A feast for the three days of the writing of the Book of the Law
A feast for Tahuti and the child of the Prophet secret O Prophet
A feast for the Supreme Ritual and a feast for the Equinox of the Gods
A feast for fire and a feast for water a feast for life and a greater feast for death
A feast every day in your hearts in the joy of my rapture
A feast every night unto Nu and the pleasure of uttermost delight
Aye feast rejoice there is no dread hereafter There is the dissolution and eternal ecstasy in the kisses of Nu
There is death for the dogs
Dost thou fail Art thou sorry Is fear in thine heart
Where I am these are not
Pity not the fallen I never knew them I am not for them I console not I hate the consoled and the consoler
I am unique and conqueror I am not of the slaves that perish Be they damned and dead Amen This is of the four there is a fifth who is invisible and therein am I as a babe in an egg
Blue am I and gold in the light of my bride but the red gleam is in my eyes and my spangles are purple and green
Purple beyond purple it is the light higher than eyesight
There is a veil that veil is black It is the veil of the modest woman it is the veil of sorrow and the pall of death this is none of me Tear down that lying spectre of the centuries veil not your vices in virtuous words these vices are my service ye do well and I will reward you here and hereafter
Fear not o prophet when these words are said thou shalt not be sorry Thou art emphatically my chosen and blessed are the eyes that thou shalt look upon with gladness But I will hide thee in a mask of sorrow they that see thee shall fear thou art fallen but I lift thee up
Nor shall they who cry aloud their folly that thou meanest nought avail thou shall reveal it thou availest they are the slaves of because They are not of me The stops as thou wilt the letters change them not in style or value
Thou shalt obtain the order and value of the English Alphabet thou shalt find new symbols to attribute them unto
Begone ye mockers even though ye laugh in my honour ye shall laugh not long then when ye are sad know that I have forsaken you
He that is righteous shall be righteous still he that is filthy shall be filthy still
Yea deem not of change ye shall be as ye are and not other Therefore the kings of the earth shall be Kings for ever the slaves shall serve There is none that shall be cast down or lifted up all is ever as it was Yet there are masked ones my servants it may be that yonder beggar is a King A King may choose his garment as he will there is no certain test but a beggar cannot hide his poverty
Beware therefore Love all lest perchance is a King concealed Say you so Fool If he be a King thou canst not hurt him
Therefore strike hard and low and to hell with them master
There is a light before thine eyes o prophet a light undesired most desirable
I am uplifted in thine heart and the kisses of the stars rain hard upon thy body
Thou art exhaust in the voluptuous fullness of the inspiration the expiration is sweeter than death more rapid and laughterful than a caress of Hells own worm
Oh thou art overcome we are upon thee our delight is all over thee hail hail prophet of Nu prophet of Had prophet of Ra Hoor Khu Now rejoice now come in our splendour and rapture Come in our passionate peace and write sweet words for the Kings
I am the Master thou art the Holy Chosen One
Write and find ecstasy in writing Work and be our bed in working Thrill with the joy of life and death Ah thy death shall be lovely whoso seeth it shall be glad Thy death shall be the seal of the promise of our age long love Come lift up thine heart and rejoice We are one we are none
Hold Hold Bear up in thy rapture fall not in swoon of the excellent kisses
Harder Hold up thyself Lift thine head breathe not so deep die
Ah Ah What do I feel Is the word exhausted
There is help and hope in other spells Wisdom says be strong Then canst thou bear more joy Be not animal refine thy rapture If thou drink drink by the eight and ninety rules of art if thou love exceed by delicacy and if thou do aught joyous let there be subtlety therein
But exceed exceed
Strive ever to more and if thou art truly mine and doubt it not an if thou art ever joyous death is the crown of all
Ah Ah Death Death thou shalt long for death Death is forbidden o man unto thee
The length of thy longing shall be the strength of its glory He that lives long and desires death much is ever the King among the Kings
Aye listen to the numbers and the words
four six three eight A B K two four A L G M O R three Y X twentyfour eightynine R P S T O V A L What meaneth this o prophet Thou knowest not nor shalt thou know ever There cometh one to follow thee he shall expound it But remember o chosen one to be me to follow the love of Nu in the star lit heaven to look forth upon men to tell them this glad word
O be thou proud and mighty among men
Lift up thyself for there is none like unto thee among men or among Gods Lift up thyself o my prophet thy stature shall surpass the stars They shall worship thy name foursquare mystic wonderful the number of the man and the name of thy house four hundred and eighteen
The end of the hiding of Hadit and blessing and worship to the prophet of the lovely Star
Abrahadabra the reward of Ra Hoor Khut
There is division hither homeward there is a word not known Spelling is defunct all is not aught Beware Hold Raise the spell of Ra Hoor Khuit
Now let it be first understood that I am a god of War and of Vengeance I shall deal hardly with them
Choose ye an island
Fortify it
Dung it about with enginery of war
I will give you a war engine
With it ye shall smite the peoples and none shall stand before you
Lurk Withdraw Upon them this is the Law of the Battle of Conquest thus shall my worship be about my secret house
Get the stele of revealing itself set it in thy secret temple and that temple is already aright disposed and it shall be your Kiblah for ever It shall not fade but miraculous colour shall come back to it day after day Close it in locked glass for a proof to the world
This shall be your only proof I forbid argument Conquer That is enough I will make easy to you the abstruction from the ill ordered house in the Victorious City Thou shalt thyself convey it with worship o prophet though thou likest it not Thou shalt have danger and trouble Ra Hoor Khu is with thee Worship me with fire and blood worship me with swords and with spears Let the woman be girt with a sword before me let blood flow to my name Trample down the Heathen be upon them o warrior I will give you of their flesh to eat
Sacrifice cattle little and big after a child
But not now
Ye shall see that hour o blessed Beast and thou the Scarlet Concubine of his desire
Ye shall be sad thereof
Deem not too eagerly to catch the promises fear not to undergo the curses Ye even ye know not this meaning all
Fear not at all fear neither men nor Fates nor gods nor anything Money fear not nor laughter of the folk folly nor any other power in heaven or upon the earth or under the earth Nu is your refuge as Hadit your light and I am the strength force vigour of your arms
Mercy let be off damn them who pity Kill and torture spare not be upon them
That stele they shall call the Abomination of Desolation count well its name and it shall be to you as seven hundred and eighteen
Why Because of the fall of Because that he is not there again
Set up my image in the East thou shalt buy thee an image which I will show thee especial not unlike the one thou knowest And it shall be suddenly easy for thee to do this
The other images group around me to support me let all be worshipped for they shall cluster to exalt me I am the visible object of worship the others are secret for the Beast and his Bride are they and for the winners of the Ordeal x What is this Thou shalt know
For perfume mix meal and honey and thick leavings of red wine then oil of Abramelin and olive oil and afterward soften and smooth down with rich fresh blood
The best blood is of the moon monthly then the fresh blood of a child or dropping from the host of heaven then of enemies then of the priest or of the worshippers last of some beast no matter what
This burn of this make cakes and eat unto me This hath also another use let it be laid before me and kept thick with perfumes of your orison it shall become full of beetles as it were and creeping things sacred unto me
These slay naming your enemies and they shall fall before you
Also these shall breed lust and power of lust in you at the eating thereof
Also ye shall be strong in war
Moreover be they long kept it is better for they swell with my force All before me
My altar is of open brass work burn thereon in silver or gold
There cometh a rich man from the West who shall pour his gold upon thee
From gold forge steel
Be ready to fly or to smite
But your holy place shall be untouched throughout the centuries though with fire and sword it be burnt down and shattered yet an invisible house there standeth and shall stand until the fall of the Great Equinox when Hrumachis shall arise and the double wanded one assume my throne and place Another prophet shall arise and bring fresh fever from the skies another woman shall awake the lust and worship of the Snake another soul of God and beast shall mingle in the globed priest another sacrifice shall stain the tomb another king shall reign and blessing no longer be poured To the Hawk headed mystical Lord
The half of the word of Heru ra ha called Hoor pa kraat and Ra Hoor Khut
Then said the prophet unto the God
I adore thee in the song I am the Lord of Thebes and I The inspired forth speaker of Mentu For me unveils the veiled sky The self slain Ankh af na khonsu Whose words are truth I invoke I greet Thy presence O Ra Hoor Khuit Unity uttermost showed I adore the might of Thy breath Supreme and terrible God Who makest the gods and death To tremble before Thee I I adore thee Appear on the throne of Ra Open the ways of the Khu Lighten the ways of the Ka The ways of the Khabs run through To stir me or still me Aum let it fill me
So that thy light is in me and its red flame is as a sword in my hand to push thy order There is a secret door that I shall make to establish thy way in all the quarters these are the adorations as thou hast written as it is said The light is mine its rays consume Me I have made a secret door Into the House of Ra and Tum Of Khephra and of Ahathoor I am thy Theban O Mentu The prophet Ankh af na khonsu By Bes na Maut my breast I beat By wise Ta Nech I weave my spell Show thy star splendour O Nuit Bid me within thine House to dwell O winged snake of light Hadit Abide with me Ra Hoor Khuit
All this and a book to say how thou didst come hither and a reproduction of this ink and paper for ever for in it is the word secret and not only in the English and thy comment upon this the Book of the Law shall be printed beautifully in red ink and black upon beautiful paper made by hand and to each man and woman that thou meetest were it but to dine or to drink at them it is the Law to give Then they shall chance to abide in this bliss or no it is no odds Do this quickly
But the work of the comment That is easy and Hadit burning in thy heart shall make swift and secure thy pen
Establish at thy Kaaba a clerk house all must be done well and with business way
The ordeals thou shalt oversee thyself save only the blind ones Refuse none but thou shalt know and destroy the traitors I am Ra Hoor Khuit and I am powerful to protect my servant Success is thy proof argue not convert not talk not over much Them that seek to entrap thee to overthrow thee them attack without pity or quarter and destroy them utterly Swift as a trodden serpent turn and strike Be thou yet deadlier than he Drag down their souls to awful torment laugh at their fear spit upon them
Let the Scarlet Woman beware If pity and compassion and tenderness visit her heart if she leave my work to toy with old sweetnesses then shall my vengeance be known I will slay me her child I will alienate her heart I will cast her out from men as a shrinking and despised harlot shall she crawl through dusk wet streets and die cold and an hungered
But let her raise herself in pride Let her follow me in my way Let her work the work of wickedness Let her kill her heart Let her be loud and adulterous Let her be covered with jewels and rich garments and let her be shameless before all men
Then will I lift her to pinnacles of power then will I breed from her a child mightier than all the kings of the earth I will fill her with joy with my force shall she see and strike at the worship of Nu she shall achieve Hadit
I am the warrior Lord of the Forties the Eighties cower before me and are abased I will bring you to victory and joy I will be at your arms in battle and ye shall delight to slay Success is your proof courage is your armour go on go on in my strength and ye shall turn not back for any
This book shall be translated into all tongues but always with the original in the writing of the Beast for in the chance shape of the letters and their position to one another in these are mysteries that no Beast shall divine Let him not seek to try but one cometh after him whence I say not who shall discover the Key of it all Then this line drawn is a key then this circle squared in its failure is a key also And Abrahadabra It shall be his child and that strangely Let him not seek after this for thereby alone can he fall from it
Now this mystery of the letters is done and I want to go on to the holier place
I am in a secret fourfold word the blasphemy against all gods of men
Curse them Curse them Curse them
With my Hawks head I peck at the eyes of Jesus as he hangs upon the cross
I flap my wings in the face of Mohammed and blind him
With my claws I tear out the flesh of the Indian and the Buddhist Mongol and Din
Bahlasti Ompehda I spit on your crapulous creeds
Let Mary inviolate be torn upon wheels for her sake let all chaste women be utterly despised among you
Also for beautys sake and loves
Despise also all cowards professional soldiers who dare not fight but play all fools despise
But the keen and the proud the royal and the lofty ye are brothers
As brothers fight ye
There is no law beyond Do what thou wilt
There is an end of the word of the God enthroned in Ras seat lightening the girders of the soul
To Me do ye reverence to me come ye through tribulation of ordeal which is bliss
The fool readeth this Book of the Law and its comment and he understandeth it not
Let him come through the first ordeal and it will be to him as silver
Through the second gold
Through the third stones of precious water
Through the fourth ultimate sparks of the intimate fire
Yet to all it shall seem beautiful Its enemies who say not so are mere liars
There is success
I am the Hawk Headed Lord of Silence and of Strength my nemyss shrouds the night blue sky
Hail ye twin warriors about the pillars of the world for your time is nigh at hand
I am the Lord of the Double Wand of Power the wand of the Force of Coph Nia but my left hand is empty for I have crushed an Universe and nought remains
Paste the sheets from right to left and from top to bottom then behold
There is a splendour in my name hidden and glorious as the sun of midnight is ever the son
The ending of the words is the Word Abrahadabra
The Book of the Law is Written and Concealed Aum Ha
Do what thou wilt shall be the whole of the Law
The study of this Book is forbidden It is wise to destroy this copy after the first reading
Whosoever disregards this does so at his own risk and peril These are most dire
Those who discuss the contents of this Book are to be shunned by all as centres of pestilence
All questions of the Law are to be decided only by appeal to my writings each for himself
There is no law beyond Do what thou wilt
Love is the law love under will"""

# Tokenize
liber_al_tokens = tokenize_english(LIBER_AL)
print(f"Liber AL vel Legis tokens: {len(liber_al_tokens)}")

# Also split by chapter for targeted testing
# We'll just use full text for now

# P19 key
P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

# === P19 KEY CHECK against Liber AL ===
print("\n" + "="*80)
print("P19 KEY vs LIBER AL vel Legis")
print("="*80)

best_m_overall = 0
best_o_overall = 0
lat = liber_al_tokens
for offset in range(len(lat) - 42):
    text_slice = lat[offset:offset+43]
    matches = sum(1 for i in range(43) if text_slice[i] == P19_KEY[i])
    if matches > best_m_overall:
        best_m_overall = matches
        best_o_overall = offset

print(f"Best direct match: offset={best_o_overall}, {best_m_overall}/43")
# Show the text there
print(f"  Text: {to_english(lat[best_o_overall:best_o_overall+43])}")
print(f"  Key:  {to_english(P19_KEY)}")

# Also check diff patterns at best offset
diff = [(P19_KEY[i] - lat[best_o_overall+i]) % 29 for i in range(43)]
print(f"  Diff: {diff}")
print(f"  Diff as text: {to_english(diff)}")
print(f"  Zeros: {diff.count(0)}/43")

# === Running key test against unsolved pages ===
print("\n" + "="*80)
print("LIBER AL as RUNNING KEY for UNSOLVED PAGES")
print("="*80)

UNSOLVED = list(range(18, 55))
results = []

for pg in UNSOLVED:
    cipher = load_page(pg)
    if cipher is None:
        continue
    n = len(cipher)
    
    if len(lat) < n:
        continue
    
    max_offset = len(lat) - n
    for offset in range(max_offset + 1):
        key_slice = lat[offset:offset+n]
        
        for mode_name, op in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            plain = [op(c,k) for c,k in zip(cipher, key_slice)]
            ic = ioc(plain)
            
            if (n > 200 and ic > 1.30) or (n <= 200 and ic > 1.50):
                text = to_english(plain[:60])
                results.append((ic, f"P{pg:02d} off={offset} {mode_name} n={n}", text))

# F-skip tests
for pg in UNSOLVED:
    cipher = load_page(pg)
    if cipher is None:
        continue
    n = len(cipher)
    
    for fmode in ['sub', 'add', 'beau']:
        plain = []
        k_idx = 0
        for c in cipher:
            if c == 0:
                plain.append(0)
            else:
                k = lat[k_idx % len(lat)]
                if fmode == 'sub':
                    plain.append((c - k) % 29)
                elif fmode == 'add':
                    plain.append((c + k) % 29)
                elif fmode == 'beau':
                    plain.append((k - c) % 29)
                k_idx += 1
        
        ic = ioc(plain)
        if (n > 200 and ic > 1.30) or (n <= 200 and ic > 1.50):
            text = to_english(plain[:60])
            results.append((ic, f"P{pg:02d} FSKIP-{fmode.upper()} n={n}", text))

# Print results
results.sort(key=lambda x: -x[0])
print(f"\nResults: {len(results)} hits")
for ic, desc, text in results[:30]:
    print(f"  IoC={ic:.4f}  {desc}")
    print(f"    {text}")

if not results:
    print("  NO significant results!")

print("\nDone.")
