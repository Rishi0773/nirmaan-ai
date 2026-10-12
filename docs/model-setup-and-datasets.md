# NIRMAAN AI: Model Setup, Datasets & Academic Limitations

This guide documents the Computer Vision models, dataset configurations, training procedures, and academic limitations of **NIRMAAN AI: Garbage Hotspot Prioritization**.

---

## 1. Computer Vision Architecture

NIRMAAN AI uses a dual-stage vision and image-processing pipeline:

1. **Object Detection (YOLOv8 by Ultralytics)**:
   - Detects individual waste items in the image.
   - Outputs bounding boxes, detected object classes, and confidence scores.
   - Supported standard waste classes:
     - `plastic` (bottles, bags, packaging)
     - `paper` (cartons, newspapers, cups)
     - `organic` (food waste, fruit peels, yard waste)
     - `metal` (beverage cans, scrap metal)
     - `glass` (broken bottles, glassware)
     - `hazardous` (e-waste, chemicals, medical waste)
     - `mixed_trash` (unsegregated municipal litter)

2. **OpenCV Contour & Coverage Analysis**:
   - Converts image to HSV / LAB color space.
   - Extracts waste contours using adaptive thresholding and morphological operations.
   - Computes the **Waste Area Ratio**:
     $$\text{Coverage Ratio} = \frac{\text{Pixel Area occupied by Waste}}{\text{Total Image Pixel Area}} \times 100\%$$
   - Combines object count $N$ and coverage percentage $C$ into an explainable 3-tier severity classification:
     - **Low**: $N \le 2$ and $C < 15\%$
     - **Medium**: $3 \le N \le 6$ or $15\% \le C < 40\%$
     - **High**: $N \ge 7$ or $C \ge 40\%$ or presence of `hazardous` waste

---

## 2. Model Weights & Fallback Strategy

The application handles YOLOv8 model loading gracefully via `src/ml/detector.py`:

- **Custom Weights Path**: `data/models/yolov8_waste_best.pt`
- **Pretrained Fallback Path**: Standard `yolov8n.pt` (automatically cached by Ultralytics)
- **Heuristic Demonstration Mode**: If no GPU / PyTorch weights can be initialized, the system falls back to an OpenCV color-saliency and edge-based detector that produces real calculated bounding boxes, confidence values, and coverage ratios without crashing.
- **Model Transparency Banner**: The UI explicitly informs the user whether inference is being powered by:
  1. `Custom Fine-tuned YOLOv8 (TACO/TrashNet)`
  2. `Base YOLOv8 (COCO Litter Detection)`
  3. `Demonstration Heuristic Mode (OpenCV Saliency)`

Never is a mock result fabricated or presented as real fine-tuned YOLO output without explicit label.

---

## 3. Dataset Documentation & Limitations

### 3.1 TACO (Trash Annotations in Context)
- **Source**: Pedro F. Proença and Pedro Simões, *TACO: Trash Annotations in Context for Litter Detection*, 2020.
- **License**: CC BY 4.0
- **Format**: COCO JSON format with 60 fine-grained categories mapped into 6 super-categories.
- **Academic Limitation**: TACO focuses heavily on coastal, park, and roadside litter (individual bottles, cigarette butts) photographed close-up. It has limited representation of large overflowing Indian municipal dhalos / blackspots with mixed wet and dry decomposition.

### 3.2 TrashNet
- **Source**: Gary Thung and Mindy Yang, *Classification of Trash for Recyclability Status*, Stanford University, 2016.
- **Classes**: Glass, Paper, Cardboard, Plastic, Metal, Trash (2,527 images).
- **Academic Limitation**: TrashNet images are captured on clean white posterboard backgrounds under controlled indoor lighting. Models trained purely on TrashNet fail on outdoor street images due to complex asphalt, dirt, and foliage backgrounds.

### 3.3 Synthetic & Simulated Bengaluru Historical Records
- **Simulated Records**: For prototype validation, spatial reports across Bengaluru wards (e.g., Koramangala, Indiranagar, Malleshwaram, Whitefield, Jayanagar) are simulated using realistic coordinates and temporal distributions.
- **Academic Demarcation**: All simulated database records contain `is_simulated = 1` in the database. The UI displays an indicator on every simulated record to ensure no synthetic data is misrepresented as genuine municipal observations.

---

## 4. How to Train or Fine-tune Custom Weights on Google Colab

1. Open a new Google Colab notebook with GPU runtime enabled.
2. Install Ultralytics:
   ```bash
   pip install ultralytics
   ```
3. Download the TACO dataset or prepared YOLO-formatted dataset:
   ```python
   from ultralytics import YOLO

   # Load pretrained nano model
   model = YOLO("yolov8n.pt")

   # Train on custom waste dataset
   results = model.train(
       data="waste_dataset.yaml",
       epochs=50,
       imgsz=640,
       batch=16,
       name="nirmaan_yolov8_waste"
   )
   ```
4. Download `runs/detect/nirmaan_yolov8_waste/weights/best.pt` and place it in `data/models/yolov8_waste_best.pt` in the NIRMAAN AI project directory.
