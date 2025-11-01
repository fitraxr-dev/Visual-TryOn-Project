# Dataset Information

## Head Pose Detection Training

Proyek ini menggunakan cascade classifiers yang telah dilatih menggunakan dataset **BIWI Kinect Head Pose Database**.

### Dataset Source

**BIWI Kinect Head Pose Database**
- **URL**: https://www.kaggle.com/datasets/kmader/biwi-kinect-head-pose-database
- **Description**: Dataset ini berisi RGB-D images dan ground truth head pose annotations dari 24 subjek yang berbeda
- **Usage**: Dataset digunakan untuk training cascade classifiers (HAAR dan LBP) untuk head detection

### Trained Models

Hasil training yang tersedia di folder `models/`:

1. **haar_biwi_cascade.xml**
   - Cascade classifier menggunakan HAAR features
   - Dilatih menggunakan positive samples dari BIWI dataset
   - Cocok untuk deteksi kepala dengan akurasi tinggi

2. **lbp_biwi_cascade.xml**
   - Cascade classifier menggunakan LBP (Local Binary Pattern) features
   - Lebih cepat daripada HAAR namun dengan sedikit trade-off pada akurasi
   - Dilatih menggunakan positive samples dari BIWI dataset

### Hat Assets

Folder `assets/hats/` berisi model-model topi dalam format PNG dengan alpha channel yang dapat di-overlay pada kepala yang terdeteksi.

### Citation

Jika Anda menggunakan dataset BIWI untuk penelitian atau pengembangan lebih lanjut, mohon sitasi paper aslinya:

```
Fanelli, G., Dantone, M., Gall, J., Fossati, A., & Van Gool, L. (2013). 
Random forests for real time 3d face analysis. 
International Journal of Computer Vision, 101(3), 437-458.
```

### Training Details

- Training dilakukan menggunakan OpenCV's `opencv_traincascade` tool
- Positive samples: Extracted dari BIWI faces_0 directory
- Negative samples: Background images tanpa kepala manusia
- Parameter training dapat dilihat di file markdown hasil training (jika tersedia)

### Notes

- Dataset BIWI asli dan file-file training intermediate (negatives_biwi, samples_biwi.vec, dll) **tidak** disertakan dalam repository ini untuk menghemat space
- Hanya cascade classifiers hasil akhir yang disertakan untuk keperluan inference/detection
- Untuk melatih ulang model, silakan download dataset dari link Kaggle di atas
