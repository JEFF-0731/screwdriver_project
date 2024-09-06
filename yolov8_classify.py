from ultralytics import YOLO
def train():
    # Load a model
    model = YOLO("yolov8s-cls.pt")  # load a pretrained model (recommended for training)

# Train the model
    results = model.train(data=r"D:\Screwdriver_Data\0722_trainingset", epochs=100, imgsz=160)

if __name__ == "__main__":
    train()