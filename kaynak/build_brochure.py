from pathlib import Path
from html import escape
import json, math, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
(ROOT/'tmp/pdfs').mkdir(parents=True,exist_ok=True)
OUT = ROOT / 'You_Talking_Tanitim_ve_Mimari.pdf'
IMG = ROOT / 'gorseller/You_Talking_Konsept.png'
if not IMG.exists():
    IMG = ROOT / 'gorseller/You_Talking_Konsept_v1.png'
FONT = Path(os.environ.get('YT_FONT_DIR', '/Users/emre/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype'))
pdfmetrics.registerFont(TTFont('Body', str(FONT/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('Bold', str(FONT/'DejaVuSans-Bold.ttf')))
W,H = 595.276,841.89
M,CW = 43,509.276
INK, MUTED = HexColor('#192631'), HexColor('#59656C')
PAPER, CORAL = HexColor('#F5F0E8'), HexColor('#F56849')
LAV, SAGE, LINE = HexColor('#E7E3F5'), HexColor('#DDECE5'), HexColor('#DDDCD7')
c = canvas.Canvas(str(OUT), pagesize=(W,H), pageCompression=1)
c.setTitle('You Talking | Tanıtım, Ürün ve Teknik Mimari')
c.setAuthor('You Talking - ürün konsepti')
c.setSubject('3 arkadaş + 1 yeni kişi: sesli sosyal uygulama için tasarım ve mimari önerisi')
page_no=0
y=0
log=[]

def clean(s):
    return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u00a0',' ')

def ps(size=10.3, color=INK, bold=False, leading=None):
    return ParagraphStyle('x',fontName='Bold' if bold else 'Body',fontSize=size,leading=leading or size*1.46,textColor=color,spaceAfter=0,allowWidows=0,allowOrphans=0)

def p(text,x=M,top=None,w=CW,size=10.3,color=INK,bold=False,gap=8):
    global y
    yy = y if top is None else top
    par=Paragraph(escape(clean(text)).replace('\n','<br/>'),ps(size,color,bold))
    _,hh=par.wrap(w,1000)
    if yy-hh < 49:
        raise RuntimeError(f'Page {page_no} overflow: {text[:80]} bottom {yy-hh}')
    par.drawOn(c,x,yy-hh)
    log.append({'page':page_no,'text':clean(text),'bottom':round(yy-hh,2)})
    if top is None: y=yy-hh-gap
    return hh

def start(title,sub='',section='ÜRÜN REHBERİ'):
    global page_no,y
    if page_no: c.showPage()
    page_no+=1
    c.setFillColor(PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Bold',9);c.drawString(M,H-29,'you talking')
    c.setFont('Body',7.4);c.setFillColor(MUTED);c.drawRightString(W-M,H-29,section)
    c.setStrokeColor(LINE);c.line(M,44,W-M,44)
    c.setFont('Body',7.2);c.drawString(M,29,'ÜRÜN KONSEPTİ  /  29 EYLÜL 2026  /  v1.0')
    c.setFont('Bold',8);c.drawRightString(W-M,29,f'{page_no:02d} / 24')
    c.bookmarkPage(f'p{page_no}');c.addOutlineEntry(clean(title),f'p{page_no}',level=0)
    y=H-60
    p(title,size=23,bold=True,gap=10)
    if sub:p(sub,size=10.2,color=MUTED,gap=19)
    return y

def h(text):
    global y
    y-=4;p(text,size=12.4,bold=True,gap=7)

def bullet(label,text):
    p(label,size=10.4,bold=True,gap=2)
    p(text,size=10.1,gap=11)

def callout(title,text,fill=SAGE):
    global y
    w=CW-26
    a=Paragraph(escape(clean(title)),ps(11,INK,True));_,ha=a.wrap(w,1000)
    b=Paragraph(escape(clean(text)),ps(10));_,hb=b.wrap(w,1000)
    height=ha+hb+30
    if y-height<49:raise RuntimeError(f'Callout overflow on {page_no}')
    c.setFillColor(fill);c.roundRect(M,y-height,CW,height,11,fill=1,stroke=0)
    a.drawOn(c,M+13,y-13-ha);b.drawOn(c,M+13,y-18-ha-hb)
    y-=height+13

def table(headers,rows,widths=None,size=9.2):
    global y
    widths=widths or [CW/len(headers)]*len(headers)
    data=[[Paragraph(escape(clean(v)),ps(size,white,True,size*1.3)) for v in headers]]
    data += [[Paragraph(escape(clean(v)).replace('\n','<br/>'),ps(size,INK,False,size*1.4)) for v in row] for row in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT')
    cmds=[('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),0.5,INK)]
    for r in range(1,len(data)):
        cmds += [('BACKGROUND',(0,r),(-1,r),white if r%2 else HexColor('#EEEAE4')),('LINEBELOW',(0,r),(-1,r),0.35,LINE)]
    t.setStyle(TableStyle(cmds));_,hh=t.wrap(CW,1000)
    if y-hh<49:raise RuntimeError(f'Table overflow on page {page_no}: bottom={y-hh}')
    t.drawOn(c,M,y-hh);y-=hh+14

def image_fit(path,x,top,w,h):
    im=ImageReader(str(path));iw,ih=im.getSize();scale=min(w/iw,h/ih)
    ww,hh=iw*scale,ih*scale
    c.drawImage(im,x+(w-ww)/2,top-hh,width=ww,height=hh,mask='auto')
    return hh

def box(x,top,w,hh,title,desc='',fill=white):
    c.setFillColor(fill);c.setStrokeColor(LINE);c.roundRect(x,top-hh,w,hh,9,fill=1,stroke=1)
    p(title,x=x+10,top=top-10,w=w-20,size=10,bold=True,gap=0)
    if desc:p(desc,x=x+10,top=top-29,w=w-20,size=8.3,color=MUTED,gap=0)

def arrow(x1,y1,x2,y2,color=MUTED):
    c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(1.15);c.line(x1,y1,x2,y2)
    a=math.atan2(y2-y1,x2-x1);path=c.beginPath();path.moveTo(x2,y2)
    path.lineTo(x2-5*math.cos(a-.5),y2-5*math.sin(a-.5));path.lineTo(x2-5*math.cos(a+.5),y2-5*math.sin(a+.5));path.close();c.drawPath(path,fill=1,stroke=0)

# 01 - cover
start('Tanıtım, ürün ve\nteknik mimari','Arkadaşlarınla gel, birlikte yeni biriyle tanış.','YOU TALKING / SEN KONUŞ')
p('3 arkadaş + 1 yeni kişi',size=27,bold=True,color=CORAL,gap=11)
p('Sesli sohbet. Komik hayvan başlıkları. Birlikte oluşan yeni arkadaşlıklar.',size=11.2,gap=15)
ih=image_fit(IMG,0,y,W,395);y-=ih+17
callout('Kafana göre takıl.','Üç arkadaş aynı odada buluşur. Ortak tercihlere uygun, katılmayı isteyen yeni biri dördüncü koltuğa gelir. Eğlenceyi insanlar üretir; avatarlar ve küçük etkileşimler sohbeti destekler.')
p('Bu belge bir ürün ve uygulama önerisidir. Görseller üretilmiş tasarım konseptleridir; çalışan uygulama veya kesinleşmiş geliştirme taahhüdü değildir.',size=8.7,color=MUTED)

# 02
start('Tek bakışta ürün','Ne yapıyoruz, kim için yapıyoruz, ilk olarak neyi doğruluyoruz?')
table(['Konu','Önerilen yön'],[
('Temel vaat','Arkadaş grubunun rahatlığıyla yeni biriyle tanışmanın merakını birleştirmek.'),
('Ana deneyim','Birbirini tanıyan üç kişi + karşılıklı tercihlere uyan bir yeni kişi + canlı ses.'),
('Görsel kimlik','İnsan avatarı, belirgin hayvan başlığı, konuşma hareketi ve kısa görsel tepkiler.'),
('İlk deneme','Türkçe konuşan 18+ davetli topluluk; web pilotu, mobil ürün için ortak sunucu.'),
('Başarı işareti','Hem arkadaş gruplarının hem tek gelenlerin sonraki hafta kendi istekleriyle dönmesi.')
],[112,CW-112])
h('Belge nasıl okunmalı?')
p('Kullanıcı yönü: sesli odalar, normal avatar üstüne hayvan aksesuarı, 3+1 eşleşme ve kız-erkek dengesi isteği. Öneri: kamera kapalı ilk sürüm, 18+ pilot, teknoloji seçimi, sayısal hedefler ve gelir planı. Bunlar uygulamaya geçmeden önce netleştirilecek kararlardır.')
table(['Sayfalar','İçerik'],[
('03-05','Dünya örnekleri, görsel tasarım ve ürünün farkı'),
('06-10','Özellikler, kullanıcı akışları, tercihler ve ekran davranışları'),
('11-16','Sistem mimarisi, veri modeli, eşleşme, API, ses ve moderasyon'),
('17-22','Ölçüm, operasyon, maliyet, büyüme, geliştirme ve kabul testleri'),
('23-24','Açık kararlar, yayın riski ve kaynaklar')
],[86,CW-86],size=9)
p('Araştırma kapsamı: resmî ürün sayfaları, mağaza tanıtımları ve teknik belgeler. Yalla, WePlay ve ZEPETO mağaza ekranları görsel olarak incelendi; hesap açılarak ürün içi kullanılabilirlik testi yapılmadı.',size=8.7,color=MUTED)

# 03
start('Dünya örnekleri ve tasarım dersleri','Yakın örnekler, You Talking için seçilecek parçalar ve özgün yön. [1-5]')
table(['Örnek','Gözlenen yaklaşım','You Talking için yorum'],[
('Yalla [1]','Grup sesi, oda ve oyunlar. Mağaza görsellerinde çok sayıda ikon, hediye ve oyun vurgusu.','Odaya katılma anlaşılır olsun. İlk ekranda iki ana eylem ve dört koltuk öne çıksın.'),
('WePlay [2]','Parti oyunları, sesli etkileşim, 3D avatar. Ekranlarda renkli oyun kartları.','Sohbeti açan kısa etkinliklerden yararlan; ilk sürümde tek bir kolay etkinlik yeterli.'),
('ZEPETO [3]','Kişiselleştirilen avatarlar, sanal ortamlar, sesli iletişim. Avatar ve moda belirgin.','Kullanıcının tanınan avatarını koru; hayvan aksesuarını değiştirilebilir bir ifade aracı yap.'),
('Bunch [4]','Arkadaşlarla görüntülü sohbet ve parti oyunları.','Arkadaş davetini ve tekrar buluşmayı kolaylaştır.'),
('Snapchat [5]','Grup görüntülü görüşmede yüz efektleri kullanılabiliyor.','Eğlenceli ifade fikri alınabilir; canlı kamera filtresi ayrı bir sonraki deney olsun.')
],[77,213,CW-290],size=9.1)
callout('Özgün çekirdek','You Talking için önerilen merkez: birlikte gelen üç arkadaşın, tercihleri uyumlu tek bir yeni kişiyle buluşması. Bu birleşimin dünyada benzersiz olduğu doğrulanmış değildir.',LAV)
p('Tasarım yorumu: sıcak ve ferah bir oda hissi; düşük görsel kalabalık; belirgin konuşan kişi; tek dokunuşla mikrofon ve ayrılma. Rakiplerin marka işaretleri, karakterleri ve ekranları ürün varlığı olarak kullanılmamalı.',size=9.6)

# 04
start('Uygulama böyle görünebilir','Üretilmiş konsept: ana sayfa, üç kişilik lobi ve dört kişilik canlı oda.','TASARIM KONSEPTİ')
ih=image_fit(IMG,M,y,CW,350);y-=ih+16
table(['Görsel karar','Uygulamadaki karşılığı'],[
('Sıcak bej + koyu metin','Sakin arka plan ve okunaklı ana hiyerarşi. Mercan rengi ana eylemlerde.'),
('İnsan yüzü + hayvan başlığı','Kullanıcı kimliği korunur; tavşan, ördek, kedi ve ayı aksesuarları komik ifade sağlar.'),
('Dört eşit katılımcı alanı','Yeni gelen de diğerleriyle aynı büyüklükte görünür; konuşan kişi dalgayla belirir.'),
('Hafif hareket','Konuşmada küçük kıpırdama; isteğe bağlı tepki. Hareket azaltma ve büyük yazı desteği.')
],[146,CW-146],size=9.1)
p('Bu görsel yön önerisidir. Görseldeki mikro metinler ve düğmeler prototip testinde netleştirilir; teknik durumlar ve kesin eşleşme kuralları sonraki sayfalardadır.',size=8.7,color=MUTED)

# 05
start('İki taraf da geri gelmek istemeli','Arkadaş grubuyla tek gelen kişinin beklentileri birlikte tasarlanır.')
bullet('Üç arkadaşın ihtiyacı','Mevcut muhabbetine yeni enerji katmak, ortak ilgi alanından biriyle tanışmak ve bunu birlikte yapmak. Arama sırasında arkadaş sohbeti devam eder.')
bullet('Tek gelen kişinin ihtiyacı','Boş odaları dolaşmadan sıcak bir muhabbete dahil olmak. Nasıl bir gruba girdiğini önceden görmek, ilk anda konuşmaya alan bulmak ve rahatça ayrılabilmek.')
bullet('Hayvan başlıklarının rolü','Ortak bir mizah dili ve hatırlanabilir kimlik oluşturmak. İnsanların daha rahat davranmasına yardımcı olabileceği bir varsayımdır; ilk günkü yenilik etkisinden ayrı test edilmelidir.')
bullet('Oda kültürü','İçeriden şakalar yeni geleni dışarıda bırakabilir. Karşılama sorusu herkese yönelir; cevaplamak ve mini etkinliklere katılmak isteğe bağlıdır. Kullanıcılara görünür puan verilmez.')
callout('Örnek ilk iki dakika','Deniz, üç arkadaşın odasına katılır. Herkes aynı soruyu görür: “Bir günlüğüne görünmez olsan yapacağın en gereksiz şey ne?” Sıra zorunlu değildir; isteyen pas geçer. Sonra sohbet serbestçe devam eder.')
h('Başlangıç topluluğu')
p('İlk pilotta birkaç yetişkin arkadaş grubu ve onlardan bağımsız katılımcılar kullanılır. Buluşmalar belli akşam saatlerinde yoğunlaştırılır. Her üçlü için bir tek kişi gerekir; kayıtlı kullanıcı sayısı kadar bu iki tarafın aynı anda hazır olması da önemlidir.')
p('Ekran kapalıyken de sohbet keyifli olmalı. Görsel efektler, ses kalitesi ve iyi oda atmosferinin üzerine eklenir.',size=10,bold=True)

# 06
start('İlk sürümün özellikleri','P0: gerçek kullanıcıların baştan sona deneyimi yaşayabilmesi için gerekenler.')
table(['Özellik','Davranış / fayda','Ölçüm'],[
('Arkadaş lobisi','Bağlantıyla iki arkadaşını çağır; üç kişi hazır olduğunda aramaya geç.','Lobinin üç kişiyle hazır olma oranı'),
('Ortak tercih kartı','Dil, sohbet havası ve desteklenen tercihler üç kişi tarafından onaylanır.','Tercihlerde terk / uyumlu aday oranı'),
('Karşılıklı eşleşme','Tek gelen, üç arkadaşın odasına katılacağını ve oda havasını görür.','Teklif kabulü / sesli katılım'),
('Ses ve bağlantı','Mikrofon denemesi, yerel susturma, konuşan kişi, geri bağlanma.','Katılım başarısı / kopma'),
('Altı hayvan başlığı','Tavşan, ördek, kedi, ayı, tilki, kurbağa; sade insan avatarları.','İkinci ziyarette seçim / kullanım'),
('Üç kısa tepki','Kahkaha, şaşırma, alkış; sesin üstüne binmeyen animasyon.','Kullanım / hareket kapatma'),
('Karşılama ve pas','Yeni kişi gelince ortak tanışma kartı; herkes kapatabilir.','İlk iki dakikada ayrılma'),
('Kontrol ve geri bildirim','Ayrılma, engelleme, şikâyet, ev sahibi çıkarma; iki taraflı deneyim sorusu.','Tekrar katılım / inceleme süresi')
],[102,269,CW-371],size=8.9)
callout('İlk sürümün tamamlanma tanımı','Dört gerçek kişi, geliştirici müdahalesi olmadan odaya girip konuşabilmeli; biri ayrıldığında durum doğru güncellenmeli; şikâyet gerçek bir inceleme ekranına düşmeli.')

# 07
start('Sonraki özellikler','Her yeni özellik, tekrar buluşmayı veya sohbetin kalitesini geliştirmeli.')
table(['Faz','Özellik','Neden / nasıl denenir?'],[
('P1','Yeniden konuşalım','Karşılıklı istek varsa bağlantı kurulur. Telefon numarası gerekmez; yedi gün içinde yeniden sohbet ölçülür.'),
('P1','Ortaya soru at','Komik ikilem, ortak hikâye ve ilgi soruları. Zorunlu değil; kart memnuniyeti ayrı ölçülür.'),
('P1','İki dakikalık mini oyun','İki doğru bir yalan veya ortak hikâye. Önce tek oyun; tamamlanma ve tekrar oynama izlenir.'),
('P1','Buluşma saati','Arkadaşlar saat belirler; hatırlatmayı isteyen açar. Aynı anda çevrimiçi olmayı destekler.'),
('P1','Oda havası / tema','Kamp, gece kafesi, sakin oda gibi arka planlar. Sohbet kontrollerinin yerini değiştirmez.'),
('P1','Sessiz tepki ve erişilebilirlik','Konuşmadan katılma tepkileri, yüksek kontrast, büyük yazı ve azaltılmış hareket.'),
('P2','Canlı hayvan filtresi','Kamera açma ayrı seçim. Cihaz performansı, ağ maliyeti ve kamera kullanımının katkısı test edilir.'),
('P2','Kozmetik koleksiyon','Açık içerikli başlık ve oda temaları. Temel sohbetin ücretsiz deneyimi korunur.'),
('P2','2+2 buluşma biçimi','İki arkadaş çifti arasında ayrı deney. 3+1 çalıştıktan sonra test edilir.')
],[44,145,CW-189],size=9)
p('İlk geliştirmeye büyük sanal dünya, herkese açık takipçi yarışı, içerik akışı ve hediye ekonomisi eklenmesi önerilmiyor. Bu tercihler odanın ana deneyimi doğrulandıktan sonra yeniden değerlendirilebilir.',size=9.7)

# 08
start('İki giriş, tek buluşma','Grup baştan hazır olur; tek gelen kişi oda teklifini kabul eder.')
table(['Adım','Üç arkadaş','Tek gelen kişi'],[
('01 / Hazırlık','Oda açar, iki arkadaşını davet eder.','“Bir gruba katıl” seçer.'),
('02 / Tercih','Ortak dil ve sohbet havasını belirler.','Kendi dil ve oda tercihlerini seçer.'),
('03 / Hazır','Üçü de aynı tercih sürümünü onaylar.','Üç arkadaşın odasına katılacağını görür.'),
('04 / Eşleşme','“Dördüncü gelsin” ile aramayı başlatır.','Uygun oda özetini görür; katılır veya geçer.'),
('05 / Bağlantı','Grup sürümü hâlâ geçerliyse yeni kişi gelir.','Katılım kesinleşince mikrofon kontrolüyle bağlanır.'),
('06 / Muhabbet','Dört kişi eşit katılımcı olarak konuşur.','Ortak karşılama sorusu, tepki ve serbest sohbet.'),
('07 / Sonrası','Yeni kişi ayrılırsa tekrar aramayı seçebilir.','Ayrılır, yeniden buluşma ister veya başka oda arar.')
],[67,220,CW-287],size=9.1)
h('Onay tasarımı')
p('Önerilen MVP: grubun üç üyesi tercih kartını onaylayarak bu koşullardaki katılıma önceden izin verir. Tek gelen kişi oda teklifini ayrıca kabul eder. Her aday için üç kişinin yeniden oylama yapması ilk sürümde gerekli değildir. Bu karar kullanıcı testinde değerlendirilecektir.')
callout('Kontrol kullanıcıda','Tercihler değişince grup onayı sıfırlanır. Yeni kişi araması yalnız grup hazır olduğunda başlar. Ret nedenleri veya “kaç kişi seni kabul etti” bilgisi gösterilmez. Yeni gelenin sesi, kabulden önce odaya aktarılmaz.',LAV)

# 09
start('Eşleştirme ve kız-erkek dengesi','Uygun kişiler arasından sürpriz eşleşme; açık ve karşılıklı tercihler.')
bullet('1. Kesin uygunluğu kontrol et','Aktif hesap, pilot yaş kapsamı, ortak dil, açıkça kesin seçilmiş koşullar, boş koltuk ve engelleme ilişkileri. Tek kişinin tercihleri de karşılanmalıdır.')
bullet('2. Uygun adayları sırala','Ortak ilgi ve sohbet havası dikkate alınır. Bekleme süresine zamanla ağırlık verilir; eşit adaylar arasından rastgele seçim yapılabilir. İlk sürüm için makine öğrenmesi gerekmez.')
bullet('3. Kesin koşulları koru','Uygun kişi yoksa bekleme, tercihleri düzenleme veya aramayı bitirme sunulur. Tercihler kullanıcıya sorulmadan gevşetilmez; değişiklik üç arkadaşın yeni onayını gerektirir.')
table(['Arkadaş grubunun dağılımı','Yeni kişi','Sonuç'],[
('2 erkek + 1 kadın','1 kadın','2 erkek + 2 kadın'),
('2 kadın + 1 erkek','1 erkek','2 kadın + 2 erkek'),
('3 erkek','1 kadın','3 erkek + 1 kadın'),
('3 kadın','1 erkek','3 kadın + 1 erkek')
],[243,97,CW-340],size=9.4)
p('Karma oda tercihi, her odanın tam 2-2 olacağı anlamına gelmez. Kullanıcının kendi beyanı ve seçimi esas alınır; cinsiyet sesten, fotoğraftan veya avatardan tahmin edilmez. “Belirtmek istemiyorum” yolunun eşleşmeye etkisi açıkça anlatılmalıdır.')
p('Çok dar filtreler beklemeyi uzatabilir. Gerçek veriye dayanmayan tahmini süre, sahte aday veya “%98 uyum” gibi sayılar gösterilmez.',size=9.8,bold=True)

# 10
start('Ekranlar ve davranış sözleşmesi','Görsel tasarımdan çalışan arayüze geçerken her durumun bir karşılığı olmalı.')
table(['Ekran','Ana eylem','Boş / hata / bekleme durumu'],[
('Ana sayfa','Arkadaşlarımla oda aç / Bir gruba katıl','Oturum yoksa kısa hesap akışı; izinler ihtiyaç anında istenir.'),
('Avatar','İnsan avatarı + hayvan başlığı seç','Altı hazır seçenek; varlık yüklenmezse sade avatar.'),
('Lobi','Davet paylaş; üç kişi hazır olsun','Eksik kişi sayısı açık; süresi dolan davet yenilenebilir.'),
('Ortak tercihler','Kartı onayla','Bir üye değişiklik yaparsa eski onaylar geçersiz olur.'),
('Arama','Bekle / iptal et / düzenle','Aday yoksa dürüst durum mesajı; mevcut arkadaş sohbeti sürer.'),
('Oda teklifi','Katıl / geç','Teklif süresi biterse güvenli biçimde aramaya dönülür.'),
('Canlı oda','Mikrofon, tepki, soru, ayrıl','Kopmada “Yeniden bağlanıyor”; sessiz mikrofon görünür.'),
('Sohbet sonrası','Geri bildirim / yeniden buluşma','Yanıt zorunlu değil; kişiye görünür yıldız veya puan yok.'),
('Destek / inceleme','Bildirim gönder; durumunu gör','Bildirime makbuz verilir; inceleme sonucu uygun ayrıntıyla iletilir.')
],[96,157,CW-253],size=9)
callout('Arayüz ilkeleri','Mikrofon ve ayrılma her zaman erişilebilir. Renk tek başına durum anlatmaz. Büyük dokunma alanları ve ekran okuyucu etiketleri kullanılır. Hareket azaltma ayarı animasyonları sadeleştirir.')

# 11
start('Teknik mimari','Öneri: modüler tek arka uç, yönetilen veri tabanı ve ayrı gerçek zamanlı ses katmanı.','MİMARİ')
t=y
box(M,t,240,57,'Web pilotu','React + TypeScript; davet bağlantısı',SAGE)
box(M+254,t,255,57,'Mobil uygulama','React Native + Expo development build',LAV)
box(M,t-102,315,76,'Uygulama API’si + WebSocket','Kimlik / oda / eşleştirme / yetki / şikâyet\nTypeScript + NestJS; konteyner üzerinde')
box(M+342,t-102,167,76,'Yönetilen ses SFU','LiveKit Cloud / WebRTC\nSes istemciden buraya gider',HexColor('#FBE0D5'))
arrow(M+100,t-58,M+100,t-98)
arrow(M+297,t-58,M+250,t-98)
arrow(M+433,t-58,M+426,t-98,CORAL)
p('HTTPS / WSS',x=M+111,top=t-68,w=130,size=7.5,color=MUTED)
p('Ses akışı',x=M+432,top=t-73,w=73,size=7.5,color=CORAL)
box(M,t-219,157,61,'PostgreSQL','Kalıcı durum ve işlemler',SAGE)
box(M+171,t-219,157,61,'Redis','Kuyruk / presence / hız',LAV)
box(M+342,t-219,167,61,'Nesne deposu + CDN','Avatar, başlık, uygulama varlığı')
arrow(M+78,t-178,M+78,t-214);arrow(M+247,t-178,M+247,t-214)
arrow(M+315,t-137,M+337,t-137,MUTED)
y=t-303
p('Her iki istemci de SFU’dan ses, CDN’den görsel varlık alır. API-SFU oku medya yönetim çağrısını gösterir.',size=8.4,color=MUTED,gap=9)
table(['Katman','Sorumluluk / tercih nedeni'],[
('Tek arka uç','Ayrı kod modülleri, ortak işlem sınırı. Pilot için mikroservis sayısını artırmadan hatayı izlemek kolaylaşır.'),
('Veri ve kuyruk','PostgreSQL üyelik kararının kaynağıdır. Redis yalnız geçici aday bulma ve çevrimiçi sinyallerini hızlandırır.'),
('Ses','SFU, katılımcıların medya akışlarını diğerlerine iletir. API sunucusu ses paketlerini taşımaz. [6]'),
('İstemciler','İlk doğrulama web pilotunda. Mobil uygulama aynı API’yi kullanır; LiveKit için Expo Go yerine development build gerekir. [7]')
],[96,CW-96],size=9)
p('Arka plan çalışanı: rezervasyon süresi, outbox olayları, bildirimler ve temizlik. Moderasyon paneli ayrı yetkiyle aynı API’ye bağlanır. Teknoloji ve sağlayıcılar öneridir; bu belge servis kurmaz.',size=9.3,color=MUTED)

# 12
start('Veri modeli','Mantıksal şema: son veri tabanı göçleri uygulama aşamasında üretilecek.','MİMARİ / VERİ')
table(['Varlık','Temel alanlar','Kural / ilişki'],[
('users / profiles','id, auth_subject, nickname, status, avatar_id','Kimlik sağlayıcı öznesi tekil. Yaş uygunluğu ve eşleşme tercihleri yalnız gerekli erişime açık.'),
('rooms','id, host_id, status, group_version, room_version','group_version yalnız arkadaş üçlüsü veya ortak tercihler değişince artar. room_version tüm oda olaylarını sıralar.'),
('room_members','room_id, user_id, role, joined_at, left_at','role: arkadaş veya yeni kişi. Oda+aktif kullanıcı tekil; oda kilidi altında en çok dört kişi.'),
('searches','id, room_id / user_id, prefs, version, status','Bir grup veya tek katılımcı araması. Kesin ve esnek tercihler ayrı alanlarda.'),
('group_consents','room_id, user_id, group_version','Üç arkadaşın geçerli sürüm için hazır/onay bilgisi.'),
('reservations','id, room_id, candidate_id, expires_at, state','Bir odaya bir aktif rezervasyon; sürüm ve sunucu saatiyle doğrulama.'),
('active_claims','user_id, room_id, reservation_id, kind','user_id birincil anahtar: kişi tek aktif oda veya rezervasyon hakkına sahip.'),
('blocks / reports','actor_id, target_id, room_id, reason, status','Engelleme yönlü kaydedilir; eşleştirmede iki yön de kontrol edilir. Bildirim ayrı süreçtir.'),
('outbox / audit','event_id, type, payload, created_at','İşlem sonrası olay iletimi; denetim kayıtlarında hassas alanlar azaltılır.'),
('connections / feedback','user pair, consent / session, answer','Yeniden buluşma karşılıklı; deneyim geri bildirimi kişiye görünür puan değildir.')
],[100,179,CW-279],size=8.5)
p('Tüm anahtarlar için UUID, zamanlarda UTC timestamptz önerilir. Sık oda/üye ve engel sorguları indekslenir; aktif rezervasyon için durum temelli tekillik uygulanır. Son kullanma zamanı tek başına bir indeks koşulu değildir; durum geçişi de yapılmalıdır.',size=9.3)
p('Oda - üyeler 1:N; oda - aramalar 1:N; arama - rezervasyonlar 1:N. Aktif hak aynı işlemde üyeliğe dönüşür. Yeni kişinin gelip gitmesi üçlünün tercih onayını bozmaz. Ham ses bu modelde tutulmaz.',size=9.3)

# 13
start('Eşleşmenin tutarlı kalması','Aynı aday iki odada görünmemeli; geç gelen kabul eski teklifi canlandırmamalı.','MİMARİ / DURUM')
table(['Süreç','Durumlar'],[
('Oda','FORMING > READY > LIVE; üçlü korunursa LIVE > READY. Son durum: CLOSED.'),
('Arama / teklif','SEARCHING > RESERVED > COMMITTED; yan yollar CANCELLED / EXPIRED'),
('Bağlantı','CONNECTING > CONNECTED > RECONNECTING > DISCONNECTED')
],[115,CW-115],size=9.2)
h('Atomik eşleştirme akışı')
p('1. Redis’ten aday al. 2. PostgreSQL’de oda ve adayın aktif hakkını sabit bir kilit sırasıyla kontrol et. 3. Üç arkadaşın aynı group_version için onaylı ve hazır olduğunu doğrula. 4. Engelleri ve iki tarafın tercihlerini yeniden denetle. 5. Rezervasyon ve aktif aday hakkını aynı işlemde oluştur. 6. Outbox kaydını yaz ve işlemi tamamla. [10]')
p('Aday kabulünde teklif süresi, grup sürümü, üç arkadaşın hâlâ hazır/bağlı olması, engeller ve aktif hak yeniden doğrulanır. Üyelik kesinleşir; aday hakkı oda üyeliğine dönüşür. Sonra ses erişimi verilir. Grup onayı aramadan önce alınmıştır; aday için yeni grup oylaması yoktur.')
table(['Olay','Beklenen davranış'],[
('Arkadaş ayrılır / tercih değişir','Sürüm artar; eski arama, teklif ve onaylar geçersizleşir.'),
('İki eşleştirici aynı adayı seçer','Veri tabanı tekilliği birine izin verir; diğeri yeni aday arar.'),
('Kabul ile süre dolması yarışır','Sunucu zamanı ve durum kontrolü tek sonuç üretir.'),
('Redis yeniden başlar','Geçerli aramalar kalıcı kayıttan yeniden kurulur; üyelik değişmez.')
],[177,CW-177],size=9)
p('Arkadaş koparsa yeni teklif üretimi durur. Mevcut teklif uzatılmaz; üçlü yeniden hazır olmadan katılım kesinleşmez. İptal/süre aşımında rezervasyon ve aday hakkı birlikte serbest bırakılır. İlk ses bağlantısı süresinde kurulmazsa üyelik ve medya erişimi kapatılır; üçlü yeniden aramayı seçebilir.',size=9.5)
p('Engelleme ve katılım işlemleri ortak kilit protokolüyle sıralanır. Engel önceyse kabul reddedilir; katılım önceyse aktif oda için tanımlanan susturma/ayrılma davranışı uygulanır.',size=9.5)
p('Başlangıç parametreleri: teklif 30 sn, ilk ses bağlantısı 15 sn, geçici kopma toleransı 15 sn. Bunlar pilot varsayımıdır. Veri tabanı kilidi altında ağ çağrısı yapılmaz; tekrar istekler idempotent olmalıdır.',size=9.4,bold=True)

# 14
start('API ve canlı olaylar','Örnek sözleşme; kod yazılmadan önce istemci ve sunucu aynı durum dilini kullanır.','MİMARİ / API')
table(['İşlem','Amaç / kontrol'],[
('POST /rooms','Kimliği doğrulanmış kullanıcıyla lobi oluştur.'),
('POST /rooms/:id/invites','Kısa ömürlü ve iptal edilebilir arkadaş daveti üret.'),
('PUT /rooms/:id/preferences','Yetkiyi denetle; group_version artır; eski onayları iptal et.'),
('POST /rooms/:id/ready','Üyenin güncel sürüm için onayını kaydet.'),
('POST /searches','Tam üç arkadaş veya tek kişi için arama aç. Tek aktif arama kuralı.'),
('DELETE /searches/:id','Sahip veya yetkili oda üyesinin aramasını iptal et.'),
('POST /offers/:id/accept','Yalnız rezerve aday; sürüm, süre ve üyelik yeniden doğrulanır.'),
('POST /offers/:id/decline','Aday teklifi geçer; rezervasyon serbest bırakılır. Ret nedeni gruba gösterilmez.'),
('GET /me/matching-state','Tek kişinin aktif araması, geçerli teklifi, süre sonu ve varsa oda üyeliğini döndür.'),
('POST /rooms/:id/media-token','Kesinleşmiş üyelik için oda ve kimliğe özel erişim üret.'),
('POST /rooms/:id/leave','Üyeliği ve medya erişimini kapat; gerekiyorsa ev sahibini aktar.'),
('POST /blocks, /reports','Engeli hemen uygula; bildirimi ayrı inceleme kuyruğuna yaz.')
],[228,CW-228],size=8.8)
h('WebSocket olayları')
p('room.updated, search.updated, offer.created, offer.expired, member.joined, member.left, moderation.action. Olaylar event_id, ilgili oda/arama kimliği, sürüm ve zaman taşır. Oda olayları room_version ile sıralanır. Dönüşte grup GET /rooms/:id, tek kişi GET /me/matching-state ile güncellenir.',size=9.6)
h('Hata ve güven sınırı')
p('401: oturum yok. 403: yetki yok. 409: sürüm veya aktif hak çatışması. 410: teklif süresi dolmuş. 429: hız sınırı. İstemcinin gönderdiği rol, doluluk veya cinsiyet uyumu kararı sunucuda yeniden değerlendirilir. Değiştiren isteklerde idempotency anahtarı kullanılır.',size=9.4)

# 15
start('Ses, avatar ve bağlantı yaşam döngüsü','Kamera kapalı ilk sürüm; hafif görsellerin altında gerçek zamanlı ses.','MİMARİ / MEDYA')
bullet('Sesin yolu','Mikrofon -> istemci SDK’sı -> yönetilen WebRTC SFU -> diğer üç katılımcı. Uygulama API’si kimlik ve oda yetkisini yönetir. Avatar varlıkları CDN’den yüklenir; ses paketlerine büyük görsel verisi eklenmez. [6]')
bullet('Mikrofon davranışı','İlk katılımda izin ve kısa seviye denemesi yapılır. Sessize alma görünürdür. Bir kişiyi yerel susturmak yalnız dinleyeni etkiler. Ev sahibinin çıkarma yetkisi ayrı bir sunucu işlemidir; birinin mikrofonu izinsiz açılamaz.')
bullet('Avatarın hareketi','Konuşma etkinliği küçük başlık hareketini tetikler. Kahkaha ve şaşırma kullanıcı tepkisidir; ses içeriği üzerinden duygu çıkarıldığı iddia edilmez. Düşük performanslı cihaz ve azaltılmış hareket ayarında animasyon sadeleşir.')
bullet('Erişim ve çıkarma','Oda/kimlik kapsamlı token yalnız sunucuda üretilir. Üyeliği kaldırmak, aktif ses katılımını da sonlandırmalıdır. LiveKit Cloud token iptalinde son yenilenmiş tokenların durumu dikkate alınmalı; kesin çıkarma için açık revoke_token_ts kesimi test edilmelidir. [8]')
bullet('Kopma ve yeniden bağlanma','Ağ kopması ile kullanıcının “Ayrıl” seçmesi ayrılır. Kısa toleransta mevcut kimlik korunur; yeni üyelik oluşturulmaz. Süre aşılırsa hak temizlenir. Medya webhooks ve uygulama üyeliği uzlaştırılır; tekrar ve sıra dışı webhook güvenle işlenir.')
callout('Medya test matrisi','Dört fiziksel cihaz; mobil veri ve Wi-Fi geçişi; Bluetooth kulaklık; hoparlör yankısı; mikrofon izni reddi; telefon araması; ekran kilidi; tarayıcı arka planı. Mobil arka plan davranışı platform ve SDK sürümünde ayrıca doğrulanır.',LAV)
p('Şifreli taşıma, uçtan uca şifreleme iddiasıyla aynı değildir. İlk sürüm için uçtan uca şifreleme sözü verilmez. Kayıt veya canlı transkripsiyon, ayrıca ürün ve veri işleme kararı olmadan açılmaz.',size=9.2,color=MUTED)

# 16
start('Kontrol, gizlilik ve moderasyon','Canlı sohbetin işletilmesi, uygulamanın bir parçasıdır.','MİMARİ / OPERASYON')
table(['Alan','Önerilen uygulama'],[
('Hesap ve yaş','Davetli 18+ pilot; takma ad altında kalıcı hesap. Yaş beyanı tek başına doğrulanmış yaş anlamına gelmez; gereken doğrulama yaklaşımı yayın öncesi seçilir.'),
('Yetki','Her oda işleminde aktif üyelik kontrolü. Kısa ömürlü token, sunucuda saklanan sağlayıcı anahtarları, imzalı webhook ve yönetici için MFA.'),
('Engelleme','Aday havuzundan iki yönde dışla. Bekleyen teklif iptal olur. Aktif odada kullanıcıya hemen yerel susturma ve ayrılma sunulur.'),
('Şikâyet','Oda, zaman, hedef kişi ve nedenle kayıt; kullanıcı açıklaması ve durum takibi. İncelemeye yalnız yetkili ekip erişir.'),
('İnceleme','Üç arkadaşın aynı kişiyi şikâyet etmesi otomatik hesap kapatmaz. Bağlantılı bildirimler birlikte değerlendirilir; itiraz kanalı bulunur.'),
('Veri minimizasyonu','Ham ses varsayılan olarak kaydedilmez. Hassas tercih değerleri analitik olaylara taşınmaz. Hesap silme ve saklama süreleri açıkça tanımlanır.')
],[109,CW-109],size=9.1)
h('Ses kaydı olmayan incelemenin sınırı')
p('Kayıt yoksa konuşmanın içeriğini sonradan doğrulamak her zaman mümkün olmaz. Oda olayları, kullanıcı açıklaması ve tekrar eden davranış örüntüleri değerlendirilir. Sistem “bütün ihlalleri otomatik yakalar” diye sunulmaz.')
p('Önerilen pilot saklama planı: operasyon olayları 30 gün, hata logları 14 gün, inceleme kayıtları 90 gün; ardından silme veya anonimleştirme. Bunlar hukuki zorunluluk iddiası değildir; gerçek gereksinim ve sağlayıcı ayarlarıyla netleştirilecek ürün önerileridir.',size=9.2)
p('Mağaza UGC kuralları filtreleme, raporlama ve engelleme gibi işlevleri kapsar. iOS için bu konsepti doğrudan etkileyen ayrı yayın riski sayfa 23’te açıklanmıştır. [11-12]',size=9.2,color=MUTED)

# 17
start('Başarıyı nasıl ölçeceğiz?','İndirme sayısının yanında iki tarafın tekrar kullanımını izlemek gerekir.','DOĞRULAMA')
callout('Ana gösterge önerisi','Bir haftada nitelikli 3+1 sohbeti yapan ve sonraki hafta tekrar gelen arkadaş grupları ile tek katılımcıların oranı ayrı ayrı izlenir. İki tarafın sonuçları tek ortalamada gizlenmez.')
table(['Gösterge','Tanım / neden'],[
('Nitelikli sohbet','Dört kişinin en az 5 dakika birlikte seste kalması. İlk operasyon tanımıdır; memnuniyetin kanıtı değildir.'),
('Grup W1 dönüş','İlk haftada nitelikli sohbet yapan aynı üçlünün, sonraki hafta yeniden nitelikli sohbet yapması / uygun üçlü sayısı.'),
('Tek kişi W1 dönüş','İlk hafta yeni kişi rolünde nitelikli sohbet yapanların, sonraki hafta yine katılması / uygun tek kişi sayısı.'),
('Bekleme ve kabul','Arama açılışından teklife ve ses bağlantısına kadar p50/p95 süre; teklif kabul ve iptal oranı.'),
('Dahil olma','Yeni gelenin ilk iki dakikada ayrılması ve isteğe bağlı “Kendimi dahil hissettim” yanıtı birlikte incelenir.'),
('Ses ve koruma','Başarılı bağlantı, kopma, tekrar bağlanma; bin oturum başına bildirim ve inceleme süresi.')
],[116,CW-116],size=9)
h('Olay sözlüğü')
p('lobby_created, invite_accepted, group_ready, search_started, offer_accepted, audio_connected, session_qualified, reaction_sent, report_submitted, return_session. session_id ve role ile ilişkilendirilir; analitikte gereksiz kişisel veri tutulmaz.',size=9.5)
h('Önce deney, sonra hedef')
p('Aynı gruplara sade avatar ve hayvan aksesuarı sürümleri, sıra değiştirilerek gösterilir. İkinci hafta sürekli hatırlatma yapılmadan erişim bırakılır. Altı grubun en az üçünün yeniden oda açması örnek bir erken devam eşiği olabilir; sektör standardı veya istatistiksel ispat değildir.',size=9.6)

# 18
start('Yayınlama, izleme ve işletim','Önerilen hedefler; henüz ölçülmüş hizmet seviyesi veya sağlayıcı garantisi değildir.','OPERASYON')
table(['Konu','Pilot / ilk ürün yaklaşımı'],[
('Ortamlar','Geliştirme, test ve üretim ayrı. Ayrı veri, erişim anahtarı ve ses projesi; test kullanıcıları üretim ölçümlerine karışmaz.'),
('Dağıtım','API ve worker için yönetilen konteyner; veri tabanına yakın bölge. Web statik dağıtım + CDN. Mobil istemci sürümü ayrıca yönetilir.'),
('İşlem güveni','Şema değişiklikleri geriye uyumlu yapılır. Önce genişlet, sonra istemciyi geçir, eski alanı sonraki sürümde kaldır.'),
('Gözlemlenebilirlik','Yapısal log, dağıtık iz, request_id, session_id ve hata oranı. Token, ses ve hassas tercih değerleri loglanmaz.'),
('Yedek / kurtarma','PITR destekleyen PostgreSQL hizmeti seçilir. Aylık geri yükleme provası. Öneri hedef: RPO 15 dk, RTO 4 saat.'),
('Operasyon paneli','Aktif oda sayısı, kuyruk havuzları, teklif hataları, medya bağlantısı, raporlar, sağlayıcı harcaması ve olay geçmişi.')
],[100,CW-100],size=9)
table(['Ölçüm','Başlangıç mühendislik hedefi'],[
('API','Seçilen bölgede normal yükte p95 < 500 ms; eşleşme için insan bekleme süresi hariç.'),
('Medya katılımı','İzin verilmiş cihazda p95 < 5 sn; dört cihaz ve bozuk ağ testleriyle doğrulama.'),
('Oda olayları','Durum güncellemesi p95 < 2 sn; eski sürümler istemcide uygulanmaz.'),
('Erişilebilirlik','Üretim hedefi aylık %99,5; pilotta kesintiler ve bağımlılıklar ayrı raporlanır.')
],[100,CW-100],size=9)
p('Olay müdahalesi: yeni eşleştirmeyi durdur -> mevcut sesi mümkünse koru -> hata veya veri sorununu ayır -> geri al / onar -> üyelikleri uzlaştır -> kullanıcıya durum bildir. Kontrol düzlemi yokken yeni medya tokenı verilmez.',size=9.5)

# 19
start('Kapasite ve maliyet modeli','Önce kullanım birimini ölç; sağlayıcı fiyatını sonra gerçek hacme uygula.','PLANLAMA')
callout('Temel hesap','Aylık katılımcı-dakika = günlük aktif kullanıcı x günlük ortalama bağlı dakika x 30. Örneklerde kişi başına 20 dakika/gün varsayılmıştır. Grup bekleme lobisindeki ses de kullanıma dahildir.')
table(['Senaryo','Günlük aktif','Katılımcı-dk / ay','Tepe eşzamanlı*'],[
('Küçük pilot','100','60.000','5 kişi'),
('Erken ürün','1.000','600.000','50 kişi'),
('Büyüyen ürün','10.000','6.000.000','500 kişi')
],[104,102,160,CW-366],size=9.5)
p('* Eşzamanlılık için günlük aktiflerin %5’i varsayılmıştır; gerçek dağılım ölçülmelidir. Dört kişilik dolu odalarda yaklaşık 2 / 13 / 125 eşzamanlı oda kapasitesi gerekir; üç kişilik lobiler ve bekleyen tek kişiler ayrıca modellenir.',size=9.3)
h('Aylık toplamın bileşenleri')
p('Ses planı ve kullanım aşımı + veri çıkışı / TURN gibi ilgili medya kalemleri + API/worker + PostgreSQL + Redis + depolama/CDN + izleme + destek/moderasyon + mağaza ve ödeme giderleri. Aynı kullanımın pakete dahil olduğu kalemler ikinci kez eklenmemelidir.')
p('LiveKit Cloud kullanım bazlı ölçüm kullanır; gerçek bedel plan, kota ve kaynak türüne bağlıdır. Güncel fiyatlar satın alma sırasında doğrulanmalıdır. Buradaki hacim tablosu bir fiyat teklifi değildir. [9]')
h('Bütçe kontrolü')
p('Ortam başına harcama alarmı; sahipsiz odaları kapatma; boşa açık mikrofon oturumlarını izleme; dev/test kotası; yeni kayıtları davet dalgalarıyla artırma. Düşük maliyet hedefi için ilk sürümde kamera ve sürekli kayıt açılmaz.')
p('İzlenecek birim: toplam işletim maliyeti / nitelikli sohbet sayısı. Geliştirme emeği ayrı bütçelenir. Ödeme deneyi yapılmadan gelir üzerinden maliyet karşılanacağı varsayılmaz.',size=10,bold=True)

# 20
start('Büyüme ve gelir seçenekleri','Önce yoğun bir küçük topluluk; ardından tekrar kullanım ve isteğe bağlı kozmetik.','ÜRÜN STRATEJİSİ')
bullet('İlk dağıtım','Türkçe konuşan yetişkin topluluklardan birkaç arkadaş grubu ve bağımsız katılımcı davet edilir. Haftanın belli akşamları aynı saatlerde buluşulur. Katılımcı miktarı ve oda doluluğu gerçek haliyle gösterilir.')
bullet('Davet döngüsü','Bir kullanıcı iki arkadaşını çağırır; üçlü yeni kişiyle tanışır. Karşılıklı istekle bağlantı kurulur. Bir sonraki buluşma kolaylaşır. Tek gelen kullanıcı da daha sonra kendi arkadaşlarıyla oda açabilir; ilk rolü kalıcı bir etiket değildir.')
bullet('Gelir hipotezi','Özel hayvan başlıkları, oda temaları ve koleksiyon paketleri. Paket içeriği ve fiyatı açıktır. Sohbetin temel işlevleri, engelleme ve güvenlik kontrolleri ücretli ayrıcalık haline getirilmez.')
bullet('İkinci gelir deneyi','Tekrar kullanım oluşursa kişiselleştirme üyeliği denenebilir. Ödemeye dönüşüm, iptal ve ücretsiz kullanıcı memnuniyeti birlikte izlenir. Dijital ürünlerin ödeme akışı seçilen mağazanın güncel kurallarıyla tasarlanır.')
callout('İlk öncelik','Daha çok özelliğe yatırım yapmadan önce “Üçlü tekrar geliyor mu?” ve “Tek gelen yeniden katılıyor mu?” sorularını yanıtla. Katılımcı sayısı artarken yeni gelenin deneyimi kötüleşiyorsa büyüme hızını değil oda deneyimini düzelt.',LAV)
h('İlk aşamada ayrı tutulacak fikirler')
p('Ücretli cinsiyet önceliği, görünür popülerlik puanı, hediye karşılığında konuşma sırası ve uzun yayıncı odaları ana üründen farklı teşvikler yaratabilir. Bunlar gelir sağladığı varsayılarak ilk sürüme eklenmez.')

# 21
start('Nasıl geliştireceğiz?','Bağımlılık sırasına göre teslimler; her aşamanın gözle görülür çıkış koşulu var.','YOL HARİTASI')
table(['Aşama','Teslim','Çıkış koşulu'],[
('A / Ürün ve tasarım','Ekran prototipi, yaş/kamera/tercih kararı, mağaza değerlendirmesi.','İki kullanıcı rolü de akışı anlayabiliyor; kapsam yazılı.'),
('B / Ses temeli','Dört cihazla ses, hesap, mikrofon, ayrılma ve bağlantı dönüşü.','Farklı ağlarda temel konuşma çalışıyor.'),
('C / Arkadaş lobisi','Davet, üç üye, sürümlü tercih kartı ve hazır onayları.','Eksik veya eski onaylı grupla arama başlayamıyor.'),
('D / Eşleştirme','Tek kişi akışı, rezervasyon, teklif, atomik katılım ve iptal.','Aynı kişi iki odaya düşmüyor; eski teklif kullanılamıyor.'),
('E / Tam deneyim','Avatarlar, tepkiler, karşılama, raporlama paneli, ölçüm.','Uçtan uca akış geliştirici müdahalesi olmadan çalışıyor.'),
('F / Davetli pilot','Gerçek gruplar + bağımsız yeni kişiler; iki haftalık gözlem.','Grup ve tek kişi için tekrar kullanım ve sorunlar raporlanıyor.'),
('G / Genişleme','Öncelikli hatalar, erişilebilirlik, kapasite ve yayın hazırlığı.','Pilot sonuçları sonraki yatırım kararını destekliyor.')
],[85,242,CW-327],size=9.1)
h('Ekip ve zaman varsayımı')
p('İlk çalışan pilot için iki geliştirici, kısmi ürün/tasarım ve test desteğiyle yaklaşık 8-12 haftalık bir plan başlangıç tahmini olabilir. Mevcut altyapı, native uygulama kapsamı, moderasyon hazırlığı ve mağaza kararı süreyi değiştirir. Taahhüt veya teklif değildir.')
p('Önerilen sorumluluklar: ürün sahibi kapsam ve deney; istemci geliştirici ses/arayüz; arka uç geliştirici eşleştirme/veri; tasarımcı avatar ve akış; test/operasyon sorumlusu cihaz matrisi ve kullanıcı bildirimleri.',size=9.5)

# 22
start('Kabul testleri ve pilot planı','Kod testleri ile insan deneyimi ayrı doğrulanır.','KALİTE')
table(['Test','Beklenen sonuç'],[
('Normal 3+1','Üç güncel grup onayı ve tek kişi kabulüyle dört üye; medya erişimi yalnız kesinleşen üyeye.'),
('Gruptan ayrılma','Arama ve teklif iptal; eski onay yeni üyelik oluşturamaz.'),
('Aynı aday yarışı','İki oda aynı anda seçse bile bir rezervasyon ve bir katılım.'),
('Süre / tekrar istek','Süre bitimi ile kabul yarışı tek sonuç; tekrar kabul ikinci olay yaratmaz.'),
('İlk ses bağlantısı kurulamaz','Süre sonunda adayın üyelik/aktif hakkı temizlenir; hayalet dördüncü koltuk kalmaz.'),
('Kopma / eski token','Tolerans içinde aynı kimlik; çıkarılan kişi eski erişimle geri giremez.'),
('Ev sahibi ayrılması','Yetki mevcut uygun arkadaşa aktarılır; yeni kişi otomatik arkadaş rolüne geçmez.'),
('Engel / kabul yarışı','İşlemler tek sıraya girer; iptal veya aktif oda politikası uygulanır. Toplu rapor otomatik ceza değildir.'),
('Kuyruk / Redis kaybı','Kriterler korunur; kuyruk yeniden kurulunca çift atama oluşmaz.'),
('Gerçek cihaz sesi','İzin reddi, Bluetooth, mobil veri, arka plan ve yankı senaryoları anlaşılır sonuç verir.')
],[121,CW-121],size=8.9)
h('İki haftalık kullanıcı pilotu')
p('İlk hafta: 6 arkadaş grubu ve en az 12 bağımsız tek katılımcı; farklı saatlerde deneyim ve görüşme. Sade avatar / hayvan başlığı sırasını gruplar arasında değiştir. İkinci hafta: erişimi bırak; sürekli çağırmadan kendiliğinden açılan odaları ve tekrar katılımı izle.')
p('Erken karar örneği: en az 3 grubun ve en az 4 tek katılımcının ikinci hafta dönmesi, kritik eşleşme hatasının kalmaması ve belirgin dışlanma örüntüsünün görülmemesi halinde daha büyük pilota geç. Bu küçük örneklem bir başarı kanıtı değildir; sonuçlarla eşikler yeniden seçilir.',size=9.4)

# 23
start('Açık kararlar ve yayın riski','Geliştirme başlamadan önce netleştirilecek, maliyeti ve kapsamı etkileyen konular.','KARARLAR')
callout('iOS için erken ürün kararı gerekiyor','Apple’ın 1.2 kuralı, ağırlıklı olarak rastgele veya anonim sohbet deneyimlerine dönüşen uygulamaların App Store’da yer alamayacağını belirtiyor. 3+1 eşleştirme bu değerlendirmeye konu olabilir. Takma ad yerine kalıcı hesap eklemek veya özelliğin adını değiştirmek tek başına onay garantisi değildir. [11]',HexColor('#FBE0D5'))
p('Öneri: konsepti gerçek davranışıyla değerlendirmek; arkadaş/topluluk oda katılımının ürün içindeki rolünü açıklaştırmak; ilk kullanıcı denemesini web üzerinde yapmak. Native uygulama yayını ayrı karar kapısıdır. Web pilotu diğer veri, içerik ve işletim yükümlülüklerini ortadan kaldırmaz. Google Play’in UGC şartları da ayrıca uygulanır. [12]',size=9.8)
table(['Karar','Bu belgede kullanılan varsayım'],[
('Kamera','İlk sürüm sesli ve kamera kapalı; canlı filtre sonraki ayrı deney.'),
('Yaş / ilk bölge','18+ davetli, Türkçe pilot; nihai yaş politikası belirlenmedi.'),
('Eşleşme tercihi','Az sayıda alan; kesin ve esnek tercihler görünür; tek kişinin tercihleri de geçerli.'),
('Onay','Üç arkadaş aramadan önce ortak kartı onaylar; tek gelen oda teklifini kabul eder.'),
('Cinsiyet dengesi','Tercih olarak ele alınır; 2-2 dağılım garantisi yok; seçenekler henüz kesinleşmedi.'),
('Ses kaydı','Varsayılan olarak kayıt ve transkripsiyon yok; moderasyon sınırı açıkça kabul edilir.'),
('Dağıtım / bütçe','Web pilotu ilk adım; sağlayıcı, bölge, ekip ve aylık bütçe uygulama öncesi seçilir.')
],[111,CW-111],size=9)
p('Diğer ana riskler: tek gelen kullanıcı arzı, uzun filtre beklemesi, yeni kişinin dışlanması, ses maliyeti ve moderasyon kapasitesi. Her biri pilotta ayrı göstergeyle izlenir; yalnız toplam kullanım süresine bakılmaz.',size=9.5)

# 24
start('Kaynaklar ve teslim bilgisi','Resmî kaynaklar 29 Eylül 2026 tarihinde kontrol edildi. Özellik ve kurallar değişebilir.','KAYNAKÇA')
refs=[
('[1] Yalla - resmî Google Play sayfası','https://play.google.com/store/apps/details?hl=en-GB&id=com.weieyu.yalla'),
('[2] WePlay - geliştiricinin App Store açıklaması','https://apps.apple.com/us/app/weplay-game-and-party/id1580330718'),
('[3] ZEPETO - ürün, avatar ve sesli sohbet','https://support.zepeto.me/hc/en-us/articles/900005874946-ZEPETO-Guardian-s-Guide'),
('[3a] ZEPETO - incelenen mağaza tasarımları','https://apps.apple.com/us/app/zepeto-avatar-connect-live/id1350301428'),
('[4] Bunch - resmî ürün sayfası','https://bunch.live/'),
('[5] Snapchat - grup görüşmesi ve yüz efektleri','https://help.snapchat.com/hc/en-us/articles/7012304163988-How-to-Start-a-Video-Chat-on-Snapchat'),
('[6] LiveKit - SFU mimarisi','https://docs.livekit.io/reference/internals/livekit-sfu/'),
('[7] LiveKit - Expo istemcisi','https://docs.livekit.io/transport/sdk-platforms/expo/'),
('[8] LiveKit - erişim tokenları ve iptal davranışı','https://docs.livekit.io/frontends/reference/tokens-grants/'),
('[9] LiveKit Cloud - faturalama modeli','https://docs.livekit.io/deploy/admin/billing/'),
('[10] PostgreSQL - eşzamanlılık için kilitleme','https://www.postgresql.org/docs/current/explicit-locking.html'),
('[11] Apple - App Review Guidelines, bölüm 1.2','https://developer.apple.com/app-store/review/guidelines/#user-generated-content'),
('[12] Google Play - User Generated Content','https://support.google.com/googleplay/android-developer/answer/9876937')
]
for label,url in refs:
    p(label,size=8.7,bold=True,gap=1)
    yy=y; hh=p(url,size=7.4,color=MUTED,gap=7)
    c.linkURL(url,(M,yy-hh,W-M,yy),relative=0,thickness=0)
h('Görsel ve belge hakkında')
p('Mobil ekran görseli yerleşik image_gen aracıyla bu proje için üretildi. Çalışan ürün ekranı değildir. Üretim istemi kaynak/gorsel_prompt.txt, düzenlenebilir PDF üreticisi kaynak/build_brochure.py içindedir. Konsept PNG dosyası gorseller klasöründedir.',size=8.8)
p('Kullanıcının kararları MEMORY.md içinde korunur. Özellik aşamaları, teknoloji seçimi, süreler, saklama planı ve hedef metrikler bu belgenin önerileridir. Mağaza incelemesi, canlı sistem kurulumu ve gerçek kullanıcı testleri henüz yapılmadı.',size=8.8)

assert page_no==24, page_no
c.save()
(ROOT/'tmp/pdfs/layout_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':page_no,'image':str(IMG),'text_blocks':len(log)},ensure_ascii=False))
