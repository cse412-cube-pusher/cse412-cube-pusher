# CSE412 Otonom Nesne İtme

Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic.

## Paketler ve görevler

- Mehmet: `cube_description` ve `cube_gazebo`; robot, arena, sensörler,
  Gazebo–ROS bağlantıları ve manuel sürüş.
- Kerem: SLAM, harita, konumlama ve Nav2.
- Ahmet: kamera ile küp algılama ve otonom görev yönetimi.

Bu sürüm simülasyon altyapısını içerir. Otonom görev henüz tamamlanmamıştır.

## Kurulum ve derleme

Ön koşul: ROS 2 Jazzy Desktop ve ros-dev-tools kurulu olmalıdır.
WSL kullanılıyorsa her yeni PowerShell terminalinde önce:

```powershell
wsl -d Ubuntu-24.04
```

Depoyu `~/cube_ws/src/cse412-cube-pusher` konumuna yerleştirin.
Aşağıdaki komutlar Ubuntu terminalinde çalıştırılır.

Makinede rosdep daha önce başlatılmadıysa bir kez `sudo rosdep init` çalıştırın.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/cube_ws
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro jazzy -y
colcon build --symlink-install --packages-up-to cube_gazebo
source install/setup.bash
```

## Çalıştırma: iki terminal

Birinci Ubuntu terminali — arena, robot ve ROS köprüleri:

```bash
source ~/cube_ws/install/setup.bash
ros2 launch cube_gazebo simulation.launch.py
```

İkinci Ubuntu terminali — RViz arka planda, klavye kontrolü önde:

```bash
source ~/cube_ws/install/setup.bash
rviz2 -d "$(ros2 pkg prefix cube_gazebo)/share/cube_gazebo/config/lidar.rviz" --ros-args -p use_sim_time:=true > /tmp/cube_rviz.log 2>&1 &
ros2 run cube_gazebo keyboard_teleop.py
```

Kontrol terminaline odaklanın:
- W/S veya yukarı/aşağı ok: ileri/geri.
- A/D veya sol/sağ ok: yerinde dönüş.
- Boşluk: dur.
- Q veya Ctrl+C: klavye kontrolünden çık.

Klavye girişinde gerçek tuş bırakma olayı alınmaz; komut,
yeni hareket tuşu gelmezse zaman aşımıyla sıfırlanır.
Hemen durmak için Boşluk kullanın.

Otonom sürüş sırasında klavye kontrolünü kapatın.
Nav2 ve itme kontrolünün aynı anda /cmd_vel göndermemesi sağlanmalıdır.

Kapatırken önce robotu durdurup klavye kontrolünden çıkın;
RViz'i kapatın, birinci terminalde Ctrl+C ile simülasyonu durdurun.

## Robot ve sensörler

- Diferansiyel sürüş, iki motorlu tekerlek ve pasif arka destek.
- Önde sabit küp itici.
- LiDAR: nominal tarama yüksekliği 0.25 m, 360 derece,
  360 örnek, 10 Hz, 0.12–12 m menzil.
- RGB kamera: 640×480, 15 Hz, öne ve hafif aşağı bakar.
- Sensör hızları simülasyon zamanına göredir;
  gerçek zamanlı performans bilgisayara bağlıdır.
- Arena 6×4 m; üç renkli küp ve karşılık gelen hedef alanları içerir.

## ROS arayüzleri

| Topic | Mesaj tipi | Amaç |
|---|---|---|
| /cmd_vel | geometry_msgs/msg/Twist | Robot hız komutu |
| /odom | nav_msgs/msg/Odometry | Odometri |
| /scan | sensor_msgs/msg/LaserScan | LiDAR ölçümleri |
| /camera/image_raw | sensor_msgs/msg/Image | Kamera görüntüsü |
| /camera/camera_info | sensor_msgs/msg/CameraInfo | Kamera optik parametreleri |
| /joint_states | sensor_msgs/msg/JointState | Tekerlek eklem durumları |
| /tf | tf2_msgs/msg/TFMessage | Dinamik koordinat dönüşümleri |
| /tf_static | tf2_msgs/msg/TFMessage | Sabit koordinat dönüşümleri |
| /clock | rosgraph_msgs/msg/Clock | Simülasyon saati |

TF: odom -> base_footprint -> base_link.
Sensörler: base_link -> lidar_link ve
base_link -> camera_link -> camera_optical_frame.

map -> odom dönüşümünü SLAM veya konumlama sistemi sağlayacaktır.
Simülasyonla çalışan diğer ROS düğümlerinde use_sim_time=true kullanın.

## Yapılan kontroller

- Gazebo'da arena, robot, küpler ve hedefler görüntülendi.
- Klavye ile sürüş denendi.
- /scan mesajı alındı ve odom sabit referansıyla RViz'de gösterildi.
- Kamera görüntüsü ve 640×480 CameraInfo mesajı alındı.
- /odom mesajının yayınlandığı kontrol edildi.
- Bir küpün manuel sürüşle zeminde kayarak itildiği gözlendi.

Bunlar temel manuel kontrollerdir. Haritalama, Nav2, tüm küplerin
otonom teslimi ve tekrarlı başarı testleri henüz doğrulanmamıştır.

## Sorun giderme

- /scan veya kamera topic'leri yoksa güncel kodu derleyip simülasyonu yeniden açın.
- RViz görüntü/scan ayarlarında Reliability Policy: Best Effort kullanın.
- RViz logu: `tail -n 40 /tmp/cube_rviz.log`.
- WSLg penceresi görünmezse açık Linux işlerini kaydedip kapatın;
  PowerShell'de `wsl --shutdown` çalıştırıp Ubuntu'yu yeniden açın.
  Bu komut çalışan tüm WSL dağıtımlarını durdurur.

<!-- robot-update-2026-11-25 -->

## 25 Kasım 2026: aks referansı ve U itici

base_footprint artık sürüş tekerleklerinin ortasında, zemin seviyesindedir.
base_link aynı X-Y hizasında, z=0.13 m konumundadır.
Şasi geometrisi ve kütle merkezi base_link'e göre x=-0.08 m'dedir.
Mevcut parçaların şasiye göre yerleşimi korunmuştur.
Spawn koordinatı (-2.4, -1.4) artık aks merkezini ifade eder.

base_footprint'e göre nominal konumlar:
- Sol/sağ tekerlek merkezi: (0, +/-0.15, 0.05) m.
- Arka destek merkezi: (-0.23, 0, 0.025) m.
- LiDAR: (-0.08, 0, 0.25) m.
- Kamera optik merkezi: (0.14, 0, 0.20) m.

### Sabit ve pasif U itici

İtici öne açıktır; arka plaka ve iki sabit yan koldan oluşur.
İç açıklık 0.22 m, dış genişlik 0.26 m, yükseklik 0.14 m'dir.
Yan kolların uzunluğu 0.12 m, kalınlığı 0.02 m'dir.
Hareketli eklem veya kavrama mekanizması yoktur.
Bu ölçüler takımın tasarım seçimidir; şartnamenin zorunlu itici ölçüleri değildir.

### Tekerlek temas modeli

Tekerleklerin görsel genişliği 0.03 m olarak korunmuştur.
Çarpışma silindirlerinin genişliği merkezde 0.006 m olarak modellenmiştir.
Bu, temas geometrisinin yaklaşık temsilidir.
Yarıçap 0.05 m, tekerlek merkezleri arası mesafe 0.30 m'dir.
Kütle ve atalet değerleri görsel tekerlek boyutlarına göre korunmuştur.

### Kontrol varsayılanları

linear_speed=0.15 m/s, angular_speed=0.35 rad/s, key_timeout=0.25 s.
Bunlar klavye kontrolü değerleridir; robotun azami hız limitleri değildir.
Kısa zaman aşımı nedeniyle ilk klavye tekrarında duraksama görülebilir.
Hemen durmak için Boşluk kullanılır.

### Ölçümler ve manuel kontroller

- Aks düzeltmesinden sonra yaklaşık 56.39 derecelik yerinde dönüşte
  Gazebo X-Y yer değiştirmesi yaklaşık 0.37 mm ölçüldü.
- 0.03 m çarpışma genişliğiyle: gerçek dönüş 56.39 derece,
  odometri 51.36 derece; oransal fark yaklaşık %8.92.
- 0.006 m çarpışma genişliğiyle: gerçek dönüş 54.10 derece,
  odometri 53.08 derece; fark yaklaşık %1.88.
- Ters yöndeki dönüşte: gerçek dönüş 50.73 derece,
  odometri 49.77 derece; fark yaklaşık %1.88.
- U iticiyle manuel denemede küp kollar arasında ilerledi,
  robot geri çekildiğinde ayrıldı; gözle görülür patinaj bildirilmedi.

Bu sonuçlar sınırlı manuel testlere aittir.
Yük altında hassas odometri ve otonom teslim başarısı henüz doğrulanmamıştır.

### Navigasyon ekibine geometri notu

Boş robotu, görsel tekerlek genişliği dahil ihtiyatlı biçimde kapsayan
dikdörtgen, base_footprint veya base_link X-Y düzleminde:

[[-0.28, -0.165], [0.26, -0.165], [0.26, 0.165], [-0.28, 0.165]]

Bu sınır en dış gövdeyi kapsar; U'nun iç boşluğunu da dolu kabul eder.
Nav2 footprint/padding ayarları navigasyon ekibince güncellenmelidir.
Ortalanmış, eksenlere paralel ve arka plakaya dayanmış 0.18 m küpün
ön yüzü yaklaşık x=0.32 m'ye uzanır. Küp taşınırken boş robot footprint'i
yükü tamamen kapsamaz; yükün konumu ve yönü ayrıca hesaba katılmalıdır.
