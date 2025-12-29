---
title: "Preparing Simulated Data for AI Models"
---

# Preparing Simulated Data for AI Models

## Introduction

Simulated sensor data serves as a crucial resource for training AI models in robotics. The ability to generate large amounts of labeled training data in simulation accelerates AI development while reducing costs and risks associated with real-world data collection. This section covers the preparation of simulated sensor data for various AI applications.

## Data Formats for AI Training

### Standard AI Data Formats

#### Computer Vision Data
For vision-based AI models, simulated camera data needs to be formatted appropriately:

```python
import os
import json
import cv2
import numpy as np
from PIL import Image

class VisionDataFormatter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "images")
        self.label_dir = os.path.join(output_dir, "labels")

        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.label_dir, exist_ok=True)

    def format_for_yolo(self, image, annotations, image_id):
        """Format image and annotations for YOLO training"""
        # Save image
        image_path = os.path.join(self.image_dir, f"{image_id}.jpg")
        cv2.imwrite(image_path, image)

        # Format annotations for YOLO (normalized coordinates)
        yolo_annotations = []
        for annotation in annotations:
            class_id = annotation['class_id']
            bbox = annotation['bbox']  # [x_min, y_min, x_max, y_max]

            # Convert to YOLO format (normalized center_x, center_y, width, height)
            img_h, img_w = image.shape[:2]
            x_center = (bbox[0] + bbox[2]) / 2.0 / img_w
            y_center = (bbox[1] + bbox[3]) / 2.0 / img_h
            width = (bbox[2] - bbox[0]) / img_w
            height = (bbox[3] - bbox[1]) / img_h

            yolo_annotations.append(f"{class_id} {x_center} {y_center} {width} {height}")

        # Save annotation file
        annotation_path = os.path.join(self.label_dir, f"{image_id}.txt")
        with open(annotation_path, 'w') as f:
            f.write('\n'.join(yolo_annotations))

    def format_for_coco(self, images, annotations, dataset_name):
        """Format data in COCO format"""
        coco_format = {
            "info": {
                "description": f"Synthetic {dataset_name} Dataset",
                "version": "1.0",
                "year": 2025,
                "contributor": "Digital Twin Simulation",
                "date_created": "2025-12-24"
            },
            "licenses": [{"id": 1, "name": "MIT", "url": ""}],
            "images": [],
            "annotations": [],
            "categories": []
        }

        # Add images
        for i, img in enumerate(images):
            coco_format["images"].append({
                "id": i,
                "width": img.shape[1],
                "height": img.shape[0],
                "file_name": f"image_{i:06d}.jpg",
                "license": 1,
                "flickr_url": "",
                "coco_url": "",
                "date_captured": "2025-12-24"
            })

        # Add annotations and categories
        annotation_id = 0
        for i, ann_list in enumerate(annotations):
            for ann in ann_list:
                coco_format["annotations"].append({
                    "id": annotation_id,
                    "image_id": i,
                    "category_id": ann['category_id'],
                    "bbox": ann['bbox'],
                    "area": ann['area'],
                    "iscrowd": 0
                })
                annotation_id += 1

        return coco_format
```

#### LiDAR Data for 3D Object Detection
For 3D AI models using LiDAR data:

```python
import numpy as np
import struct

class LidarDataFormatter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def save_point_cloud_bin(self, points, filename):
        """Save point cloud in KITTI .bin format"""
        # points should be Nx4 (x, y, z, intensity)
        save_file = os.path.join(self.output_dir, filename)

        # Flatten and convert to float32
        points = points.astype(np.float32)

        # Save as binary file
        points.tofile(save_file)

    def format_for_openpcdet(self, point_clouds, labels, sequence_id):
        """Format data for OpenPCDet training"""
        for i, (pc, label) in enumerate(zip(point_clouds, labels)):
            # Save point cloud
            pc_filename = f"{sequence_id:06d}_{i:06d}.bin"
            self.save_point_cloud_bin(pc, pc_filename)

            # Save label in KITTI format
            label_filename = f"{sequence_id:06d}_{i:06d}.txt"
            label_path = os.path.join(self.output_dir, label_filename)

            with open(label_path, 'w') as f:
                for obj in label:
                    line = f"{obj['type']} {obj['truncated']} {obj['occluded']} {obj['alpha']} "
                    line += f"{obj['bbox_left']} {obj['bbox_top']} {obj['bbox_right']} {obj['bbox_bottom']} "
                    line += f"{obj['height']} {obj['width']} {obj['length']} {obj['location_x']} "
                    line += f"{obj['location_y']} {obj['location_z']} {obj['rotation_y']}\n"
                    f.write(line)
```

### Multi-Modal Data Fusion
For AI models that use multiple sensor types:

```python
class MultiModalDataFormatter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def format_fusion_data(self, camera_data, lidar_data, imu_data, labels, sample_id):
        """Format multi-modal sensor data for fusion models"""
        # Save camera image
        cam_path = os.path.join(self.output_dir, f"{sample_id}_camera.jpg")
        cv2.imwrite(cam_path, camera_data)

        # Save LiDAR point cloud
        lidar_path = os.path.join(self.output_dir, f"{sample_id}_lidar.bin")
        lidar_data.astype(np.float32).tofile(lidar_path)

        # Save IMU data
        imu_path = os.path.join(self.output_dir, f"{sample_id}_imu.json")
        with open(imu_path, 'w') as f:
            json.dump({
                'timestamp': imu_data['timestamp'],
                'linear_acceleration': imu_data['linear_acceleration'].tolist(),
                'angular_velocity': imu_data['angular_velocity'].tolist(),
                'orientation': imu_data['orientation'].tolist()
            }, f)

        # Save synchronized labels
        label_path = os.path.join(self.output_dir, f"{sample_id}_labels.json")
        with open(label_path, 'w') as f:
            json.dump(labels, f)
```

## Data Augmentation in Simulation

### Physics-Based Augmentation
Unlike real-world data augmentation, simulation allows for physics-based variations:

```python
class PhysicsBasedAugmentation:
    def __init__(self):
        self.weather_conditions = ['sunny', 'cloudy', 'rainy', 'foggy']
        self.times_of_day = ['morning', 'noon', 'afternoon', 'evening', 'night']

    def augment_weather(self, image, condition):
        """Apply weather-specific augmentations"""
        if condition == 'rainy':
            return self.add_rain_effects(image)
        elif condition == 'foggy':
            return self.add_fog_effects(image)
        elif condition == 'cloudy':
            return self.add_cloudy_effects(image)
        else:
            return image

    def add_rain_effects(self, image):
        """Add realistic rain effects to image"""
        # Add rain streaks
        rain_overlay = np.zeros_like(image)
        h, w = image.shape[:2]

        # Generate random rain streaks
        for _ in range(50):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            length = np.random.randint(10, 30)
            angle = np.random.uniform(-np.pi/6, np.pi/6)  # Slight angle

            x_end = int(x + length * np.cos(angle))
            y_end = int(y + length * np.sin(angle))

            cv2.line(rain_overlay, (x, y), (x_end, y_end), (200, 200, 200), 1)

        # Blend with original image
        augmented = cv2.addWeighted(image, 0.8, rain_overlay, 0.2, 0)
        return augmented

    def add_fog_effects(self, image):
        """Add fog effects to reduce visibility"""
        # Generate fog mask with distance-based intensity
        h, w = image.shape[:2]
        center_x, center_y = w // 2, h // 2

        # Create distance map from center
        y_coords, x_coords = np.ogrid[:h, :w]
        distances = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)

        # Normalize distances
        max_dist = np.sqrt(center_x**2 + center_y**2)
        normalized_distances = distances / max_dist

        # Apply fog based on distance
        fog_intensity = np.expand_dims(normalized_distances, axis=2) * 0.7  # Max 70% fog
        fog_color = np.full_like(image, [220, 220, 220])  # Light gray fog

        # Blend original image with fog
        foggy_image = image * (1 - fog_intensity) + fog_color * fog_intensity
        return foggy_image.astype(np.uint8)
```

### Sensor-Specific Augmentation

#### Camera Augmentation
```python
class CameraAugmentation:
    def __init__(self):
        self.camera_configs = [
            {'focal_length': 4.0, 'resolution': (640, 480)},
            {'focal_length': 8.0, 'resolution': (1280, 720)},
            {'focal_length': 12.0, 'resolution': (1920, 1080)}
        ]

    def augment_camera_parameters(self, image, config_idx):
        """Apply different camera parameters"""
        config = self.camera_configs[config_idx]

        # Apply different focal lengths (affects FOV)
        # This would typically involve warping the image

        # Apply different resolutions
        new_h, new_w = config['resolution'][1], config['resolution'][0]
        resized_image = cv2.resize(image, (new_w, new_h))

        return resized_image
```

#### LiDAR Augmentation
```python
class LidarAugmentation:
    def __init__(self):
        self.lidar_configs = [
            {'range': 30, 'fov': 360, 'resolution': 0.1},
            {'range': 100, 'fov': 360, 'resolution': 0.2},
            {'range': 150, 'fov': 180, 'resolution': 0.5}
        ]

    def augment_lidar_point_cloud(self, point_cloud, config_idx):
        """Apply different LiDAR configurations"""
        config = self.lidar_configs[config_idx]

        # Filter points based on range
        distances = np.sqrt(np.sum(point_cloud[:, :3]**2, axis=1))
        valid_mask = distances <= config['range']
        filtered_points = point_cloud[valid_mask]

        # Apply resolution effects (downsampling)
        step = max(1, int(1.0 / config['resolution']))
        downsampled_points = filtered_points[::step]

        return downsampled_points
```

## Domain Randomization

### Concept and Implementation
Domain randomization helps models generalize better by training on varied environments:

```python
import random

class DomainRandomization:
    def __init__(self):
        self.material_properties = {
            'albedo': (0.1, 1.0),  # Surface reflectance
            'roughness': (0.0, 1.0),  # Surface roughness
            'metallic': (0.0, 1.0)  # Metallic properties
        }

        self.lighting_conditions = {
            'intensity': (0.5, 2.0),
            'color_temperature': (3000, 8000),  # Kelvin
            'direction': (0, 2*np.pi)  # Random direction
        }

    def randomize_environment(self, scene_params):
        """Randomize environment parameters"""
        randomized = scene_params.copy()

        # Randomize material properties
        randomized['ground_albedo'] = random.uniform(*self.material_properties['albedo'])
        randomized['ground_roughness'] = random.uniform(*self.material_properties['roughness'])

        # Randomize lighting
        randomized['light_intensity'] = random.uniform(*self.lighting_conditions['intensity'])
        randomized['light_temperature'] = random.uniform(*self.lighting_conditions['color_temperature'])
        randomized['light_direction'] = random.uniform(*self.lighting_conditions['direction'])

        # Randomize object appearances
        randomized['object_colors'] = self.randomize_colors()
        randomized['object_textures'] = self.randomize_textures()

        return randomized

    def randomize_colors(self):
        """Generate random colors for objects"""
        colors = []
        for _ in range(10):  # Randomize up to 10 different object types
            color = [random.random() for _ in range(3)]  # RGB values 0-1
            colors.append(color)
        return colors

    def randomize_textures(self):
        """Randomize surface textures"""
        textures = ['smooth', 'rough', 'textured', 'patterned']
        return [random.choice(textures) for _ in range(10)]
```

## Synthetic Data Generation Pipeline

### Automated Dataset Creation
```python
class SyntheticDatasetGenerator:
    def __init__(self, output_dir, num_samples=10000):
        self.output_dir = output_dir
        self.num_samples = num_samples
        self.formatter = VisionDataFormatter(output_dir)
        self.augmenter = PhysicsBasedAugmentation()
        self.randomizer = DomainRandomization()

        os.makedirs(output_dir, exist_ok=True)

    def generate_dataset(self):
        """Generate synthetic dataset with annotations"""
        dataset_info = {
            'total_samples': self.num_samples,
            'generation_date': '2025-12-24',
            'simulated_conditions': [],
            'object_classes': ['robot', 'human', 'obstacle', 'furniture']
        }

        for i in range(self.num_samples):
            # Randomize environment
            env_params = self.randomizer.randomize_environment({})

            # Generate synthetic image
            synthetic_image = self.generate_synthetic_image(env_params)

            # Apply augmentation
            weather_condition = random.choice(self.augmenter.weather_conditions)
            augmented_image = self.augmenter.augment_weather(synthetic_image, weather_condition)

            # Generate annotations (in simulation, we know ground truth)
            annotations = self.generate_ground_truth_annotations(env_params)

            # Format for AI training
            self.formatter.format_for_yolo(augmented_image, annotations, f"synthetic_{i:06d}")

            # Log condition
            dataset_info['simulated_conditions'].append(weather_condition)

            if i % 1000 == 0:
                print(f"Generated {i}/{self.num_samples} samples")

        # Save dataset info
        info_path = os.path.join(self.output_dir, "dataset_info.json")
        with open(info_path, 'w') as f:
            json.dump(dataset_info, f, indent=2)

    def generate_synthetic_image(self, env_params):
        """Generate synthetic image based on environment parameters"""
        # This would interface with your simulation engine
        # For now, return a placeholder
        h, w = 480, 640
        image = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
        return image

    def generate_ground_truth_annotations(self, env_params):
        """Generate ground truth annotations for synthetic image"""
        # In simulation, we have access to perfect ground truth
        annotations = []

        # Example: Generate random bounding boxes
        num_objects = random.randint(1, 5)
        h, w = 480, 640

        for _ in range(num_objects):
            x_min = random.randint(0, w-100)
            y_min = random.randint(0, h-100)
            width = random.randint(20, 100)
            height = random.randint(20, 100)

            annotations.append({
                'class_id': random.randint(0, 3),  # 4 object classes
                'bbox': [x_min, y_min, x_min + width, y_min + height]
            })

        return annotations
```

## Quality Assurance for AI Training Data

### Data Validation
```python
class DataQualityValidator:
    def __init__(self):
        self.validation_thresholds = {
            'min_objects_per_image': 1,
            'max_objects_per_image': 20,
            'min_bbox_area': 100,  # pixels
            'max_annotation_error': 0.1  # 10% error tolerance
        }

    def validate_dataset(self, dataset_path):
        """Validate synthetic dataset quality"""
        validation_results = {
            'total_images': 0,
            'valid_images': 0,
            'average_objects_per_image': 0,
            'annotation_quality_score': 0.0,
            'issues_found': []
        }

        image_dir = os.path.join(dataset_path, "images")
        label_dir = os.path.join(dataset_path, "labels")

        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))]

        total_objects = 0
        for img_file in image_files:
            validation_results['total_images'] += 1

            # Load corresponding annotation
            base_name = os.path.splitext(img_file)[0]
            label_file = base_name + '.txt'
            label_path = os.path.join(label_dir, label_file)

            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    annotations = f.readlines()

                num_objects = len(annotations)
                total_objects += num_objects

                # Validate annotations
                if (num_objects < self.validation_thresholds['min_objects_per_image'] or
                    num_objects > self.validation_thresholds['max_objects_per_image']):
                    validation_results['issues_found'].append(
                        f"Image {img_file} has {num_objects} objects (outside threshold)"
                    )
                else:
                    validation_results['valid_images'] += 1

        if validation_results['total_images'] > 0:
            validation_results['average_objects_per_image'] = (
                total_objects / validation_results['total_images']
            )

        # Calculate quality score
        if validation_results['total_images'] > 0:
            valid_ratio = validation_results['valid_images'] / validation_results['total_images']
            validation_results['annotation_quality_score'] = valid_ratio

        return validation_results
```

## Transfer Learning Considerations

### Bridging Simulation and Reality
```python
class SimToRealTransferHelper:
    def __init__(self):
        self.sim2real_mapping = {
            'sim_noise_model': 'real_noise_characteristics',
            'sim_lighting': 'real_lighting_conditions',
            'sim_sensor_params': 'real_sensor_specs'
        }

    def generate_sim2real_report(self, sim_model_performance, real_model_performance):
        """Generate report on sim-to-real transfer performance"""
        report = {
            'simulation_performance': sim_model_performance,
            'real_world_performance': real_model_performance,
            'performance_gap': {},
            'recommendations': []
        }

        # Calculate performance gaps
        for metric in sim_model_performance.keys():
            if metric in real_model_performance:
                gap = sim_model_performance[metric] - real_model_performance[metric]
                report['performance_gap'][metric] = gap

                if gap > 0.1:  # Significant gap (>10%)
                    report['recommendations'].append(
                        f"Large gap in {metric}: consider adjusting simulation parameters"
                    )

        return report

    def suggest_simulation_improvements(self, performance_gap):
        """Suggest simulation improvements based on performance gaps"""
        suggestions = []

        if performance_gap.get('precision', 0) > 0.1:
            suggestions.append("Increase sensor noise to match real conditions")
        if performance_gap.get('recall', 0) > 0.1:
            suggestions.append("Add more diverse training scenarios")
        if performance_gap.get('mAP', 0) > 0.1:
            suggestions.append("Improve domain randomization parameters")

        return suggestions
```

## Best Practices for AI Data Preparation

### For Data Quality
- Ensure consistent coordinate frames across all sensors
- Validate temporal synchronization between sensors
- Include diverse scenarios and edge cases
- Verify annotation accuracy and completeness

### For Training Efficiency
- Balance dataset size with computational resources
- Use appropriate data loading strategies for large datasets
- Implement efficient data augmentation pipelines
- Consider data streaming for very large datasets

### For Generalization
- Apply domain randomization appropriately
- Include various environmental conditions
- Test on validation sets that mimic real conditions
- Monitor for overfitting to simulation artifacts

### For Deployment Readiness
- Validate performance on real hardware when possible
- Document simulation assumptions and limitations
- Plan for continuous learning from real-world data
- Consider safety implications of sim2real transfer

```mdx-code-block
import SimulationDiagram from '@site/src/components/simulation-diagram/SimulationDiagram';

<div className="simulation-section">
  <SimulationDiagram
    title="AI Data Preparation"
    description="How simulated sensor data is prepared for AI model training"
    type="gazebo"
  />
</div>
```

## Assessment Questions

1. What are the standard data formats used for AI training with sensor data?
2. Explain the concept of physics-based augmentation in simulation.
3. What is domain randomization and why is it important for AI training?
4. Describe the process for generating synthetic datasets with ground truth annotations.
5. What are the key considerations for ensuring good sim-to-real transfer performance?

## Chapter Summary

This chapter covered sensor simulation in digital twins:

1. Simulating various sensor types (LiDAR, cameras, IMUs) with realistic parameters
2. Creating sensor data pipelines for processing and filtering
3. Modeling noise, latency, and other realism factors
4. Preparing simulated data for AI model training

These capabilities enable the creation of realistic digital twins that can generate valuable training data for AI systems, bridging the gap between simulation and real-world deployment.