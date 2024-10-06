from ultralytics import YOLO
import cv2
import time
CAR_CLASS = 2
PLACARD_CLASS = 0
import json


def vid_inference(video_path, car_model, placard_model, quadrants=True, tag=None):
    cap = cv2.VideoCapture(video_path)

    did_first = False


    latencies = []

    #get filename from video path
    filename = video_path.split('/')[-1]
    filename = filename.split('.')[0]

    
    print("starting")
    while cap.isOpened():
        ret, frame = cap.read()
        # time.sleep(5)
        print("frame")
        print(frame)
        if not did_first:
            first_frame = frame.copy()
            did_first = True
            if tag is None:
               tag = ""
            out = cv2.VideoWriter(f'{filename}-out{tag}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (first_frame.shape[1], first_frame.shape[0]))
        if not ret:
            break
        start = time.time()
        frame = inference(frame, car_model, placard_model, quadrants=quadrants)
        end = time.time()

        latencies.append(end - start)

        out.write(frame)

        with open(f'{filename}.json', 'w') as f:
            d = {'latencies': latencies, 'average': sum(latencies) / len(latencies)}
            json.dump(d, f)
    cap.release()
    cv2.destroyAllWindows()

    #write video mp4
    
def inference(frame, car_model, placard_model, quadrants=True, threshold=0.5):
    
    car_bounding_boxes = get_bounding_boxes(frame, car_model, CAR_CLASS)

    # get car sub-images
    car_images = []
    for box in car_bounding_boxes:
        car_images.append(frame[box[1]:box[3], box[0]:box[2]])

    # check for placards in car sub-images
    for i, car_image in enumerate(car_images):
        confs = get_placard_confs(car_image, placard_model, PLACARD_CLASS, quadrants=quadrants, threshold=threshold)
        print(confs)
        if len(confs) > 0:
            #draw bounding box around CAR
            cv2.rectangle(frame, (car_bounding_boxes[i][0], car_bounding_boxes[i][1]), (car_bounding_boxes[i][2], car_bounding_boxes[i][3]), (255, 0, 0), 7)
            c = max(confs)

            #round to 2 decimal places
            c = round(c, 2)
            #write confidence
            cv2.putText(frame, str(c), (car_bounding_boxes[i][0], car_bounding_boxes[i][1]), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 7, cv2.LINE_AA)
    return frame

def get_bounding_boxes(cv2_frame_in, model, class_number, conf=False):

  MIN_WIDTH = 100
  MIN_HEIGHT = 100

  results = model(cv2_frame_in)

  bounding_boxes = []
  confs = []
  for result in results:
    boxes = result.boxes.cpu().numpy()
    for box in boxes:
      if int(box.cls) == class_number:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
    
        if x2 - x1 > MIN_WIDTH or y2 - y1 > MIN_HEIGHT:
          continue


        bounding_boxes.append((x1, y1, x2, y2))
        if conf:
          confs.append(float(box.conf[0]))

  if conf:
    return bounding_boxes, confs
  return bounding_boxes


def get_placard_confs(cv2_frame_in, model, class_number, quadrants=True, threshold=0.5):
    if not quadrants:
        placard_bounding_boxes, confs = get_bounding_boxes(cv2_frame_in, model, class_number, conf=True)
        confs = [c for c in confs if c > threshold]
        return confs
    
    #divide into quadrants
    height, width, _ = cv2_frame_in.shape
    half_height = height // 2
    half_width = width // 2
    quadrants = [(0, half_width, 0, half_height), (half_width, width, 0, half_height), (0, half_width, half_height, height), (half_width, width, half_height, height)]

    for quadrant in quadrants:
        x1, x2, y1, y2 = quadrant
        placard_bounding_boxes, confs = get_bounding_boxes(cv2_frame_in[y1:y2, x1:x2], model, class_number, conf=True)
        if len(confs) > 0:
            print("here!")
            confs = [c for c in confs if c > threshold]
            return confs
    
    return []
