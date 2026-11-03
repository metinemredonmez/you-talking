# You Talking — Proje hafızası

Son güncelleme: 29 Eylül 2026

## Kullanıcının ifade ettiği ürün yönü

- Çalışma adı: You Talking / Sen Konuş.
- Amaç, odalarda canlı sesli grup sohbetiyle eğlenmek ve komik ortak anlar yaşamak.
- Görsel fikir: normal avatarların başında tavşan, kedi, ördek gibi hayvan başlıkları, maskeleri veya aksesuarları. Kullanıcı canlı yüz filtresini de örnek verdi; kamera kapalı avatar ile gerçek yüz üzerinde canlı filtre arasında nihai seçim henüz yapılmadı.
- Temel senaryo: birbirini tanıyan üç arkadaş bir odada bulunur. Üçünün birlikte istediği özelliklere uygun yeni bir kişi, dördüncü katılımcı olarak eşleştirilir.
- Buradaki "random", tamamen filtresiz seçim olarak yorumlanmamalı: grubun tercihleriyle uyumlu kişiler arasından yeni birini bulma fikridir. Kullanıcı henüz tercih alanlarını tek tek belirlemedi.
- Kullanıcı, eşleştirmede kız–erkek dengesini özellikle istiyor. Bunun bir tercih mi yoksa zorunlu kota mı olacağı ve oda başına hedef dağılım henüz belirlenmedi.
- Kullanıcı bu fikrin proje hafızasına kaydedilmesini açıkça istedi.
- Kullanıcı, Yalla, WePlay, ZEPETO, Bunch ve Snapchat örneklerinden uygun özelliklerin birleştirilmesi ile sade özgün oda deneyimi arasında ürün görüşü istiyor. Tüm özelliklerin eklenmesine karar verilmedi.

## Değerlendirme önerileri — henüz kullanıcı kararı değil

- İlk denenecek çekirdek akış: üç arkadaş + ortak tercihler + yeni bir dördüncü kişi + hayvan aksesuarlarıyla sesli sohbet.
- Hem grubun hem tek gelen kişinin tercihleri eşleştirmede dikkate alınabilir. Tek gelen kişi, birbirini tanıyan üç kişiye katılacağını önceden görebilir ve katılımı seçebilir.
- Dil, ilgi alanı ve sohbet tarzı gibi az sayıda tercih ile başlamak; kesin kriterlerle esnek tercihleri ayırmak değerlendirilebilir.
- Cinsiyet dengesi bir eşleştirme tercihi olarak denenebilir. Üç kişilik grubun dağılımı korunurken yalnız bir yeni kişiyle her zaman 2–2 dengesi kurulamaz. Bekleme uzarsa kriterleri değiştirme kararı kullanıcıda kalmalı.
- Yeni kişiyi karşılayan kısa bir tanışma turu ve isteğe bağlı ortak sohbet sorusu, üç arkadaş arasında dışarıda kalma hissini azaltmak için denenebilir.
- Konuşunca hareket eden aksesuarlar, kahkaha/şaşırma/alkış tepkileri ve davet bağlantıları ilk deneyime uyabilir.
- İlk kapsam için oda sahibinin susturma/çıkarma, katılımcıların engelleme/şikâyet etme ve kolay ayrılma kontrolleri düşünüldü.
- Mağaza, hediyeler, büyük sanal dünyalar ve çok sayıda oyun daha sonra değerlendirilebilir; ilk denemeye dahil edilmeleri kararlaştırılmadı.
- Başarı varsayımı: görsel yenilikten sonra kullanıcıların aynı kişilerle yeniden buluşması, yeni oda açması ve arkadaş getirmesi.

## Araştırmada kullanılan benzer ürünler

Bu bağlantılar özellik örnekleridir; ürünün benzersizliğine veya ticari başarısına kanıt değildir. Değişebilecek özellikler gerektiğinde yeniden doğrulanmalı.

- Yalla: grup sesli odaları ve birlikte oyunlar. https://play.google.com/store/apps/details?hl=en-GB&id=com.weieyu.yalla
- WePlay: sesli etkileşim, parti oyunları ve 3D avatarlar. https://apps.apple.com/us/app/weplay-game-and-party/id1580330718
- ZEPETO: avatarlarla sanal ortamlarda sosyalleşme ve sesli sohbet. https://support.zepeto.me/hc/en-us/articles/900005874946-ZEPETO-Guardian-s-Guide
- Bunch: arkadaşlarla görüntülü sohbet ve parti oyunları. https://bunch.live/
- Snapchat: grup görüntülü görüşmede yüz efektleri. https://help.snapchat.com/hc/en-us/articles/7012304163988-How-to-Start-a-Video-Chat-on-Snapchat

## Açık kalan kararlar

- Kamera kapalı avatar mı, canlı kamera filtresi mi, ikisi mi?
- Grubun ve tek gelen kişinin belirleyebileceği özellikler neler?
- Cinsiyet dengesi tercihi nasıl ifade edilecek ve uyumlu kişi bulunamadığında ne gösterilecek?
- Odaya girişte onay akışı, yeni kişi arama ve oda kapasitesi ayrıntıları nasıl olacak?
- İlk hedef kitle ve ilk denemenin kapsamı nedir?

## Hazırlanan proje belgeleri ve görseller

- Kullanıcı, yeni özellikleri, dünya örneklerini, tasarımı ve tüm mimariyi içeren görselli bir tanıtım PDF'ini masaüstündeki bu klasöre istedi.
- `You_Talking_Tanitim_ve_Mimari.pdf`: 24 sayfalık ürün, tasarım ve mimari önerisi. Özellikler, 3+1 akışları, veri modeli, API, ses, moderasyon, maliyet hacimleri, yol haritası, test planı ve resmî kaynaklar içerir.
- `gorseller/You_Talking_Konsept.png`: image_gen ile üretilen üç ekranlı mobil konsept. Sıcak bej, mercan düğmeler, normal insan avatarları ve hayvan başlıkları. Çalışan uygulama ekranı değildir.
- `kaynak/build_brochure.py`: PDF'in düzenlenebilir üretim kaynağı. `kaynak/gorsel_prompt.txt`: görsel üretim istemi.
- Belgede önerilen akış: üç arkadaş aynı tercih sürümünü arama öncesi onaylar; yeni kişi oda teklifini ayrıca kabul eder. Her yeni aday için grup oylaması yoktur. Bu hâlâ ürün önerisidir.
- Önerilen mimari: önce web pilotu, ileride ortak API kullanan mobil istemci; modüler TypeScript API, PostgreSQL, geçici Redis kuyruğu, yönetilen LiveKit ses servisi. Hiçbiri henüz kurulmadı.
- Apple'ın mevcut 1.2 kuralı rastgele/anonim sohbet deneyimlerini kısıtladığından iOS yayını önemli açık karardır. Kalıcı hesap veya özellik adı değişikliği tek başına onay garantisi değildir; kaynak PDF'de verilmiştir.
- Kullanıcı isim hakkında görüş sordu. Asistan, logoda "You Talking?" ve altında "Kafana göre takıl." önerdi; soru işaretli yazım henüz kullanıcı tarafından kesinleştirilmedi.
