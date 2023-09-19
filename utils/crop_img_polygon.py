from PIL import Image, ImageDraw
import numpy as np
def _polygon_crop(
    img_array: np.ndarray,
    polygon: np.ndarray
):
    # region 1. Create mask polygn
    mask_img = Image.new('L', (img_array.shape[1], img_array.shape[0]), 0)
    ImageDraw.Draw(mask_img).polygon(polygon, outline=1, fill=1)
    mask = np.array(mask_img)
    # endregion

	# region Merge original image and mask image
    new_img_array = np.empty(img_array.shape, dtype='uint8')
    new_img_array[:,:,:3] = img_array[:,:,:3]

    # new_img_array[:,:,:0] = new_img_array[:,:,0] * mask
    # new_img_array[:,:,:1] = new_img_array[:,:,1] * mask
    # new_img_array[:,:,:2] = new_img_array[:,:,2] * mask
    # mask = mask*255
    # new_img_array[:,:,3] = [[img_array[:, :, 3][i][j] if mask[i][j] == 255 else mask[i][j] for j in range(len(mask[i]))] for i in range(len(mask))] 
	# endregion
    return new_img_array

if __name__ == '__main__':
    # region get bboxes
	bbox = [[245, 8], [293, 11], [256, 614], [209, 612]]
	(tl, tr, br, bl) = bbox
	tl = (int(tl[0]), int(tl[1]))
	tr = (int(tr[0]), int(tr[1]))
	br = (int(br[0]), int(br[1]))
	bl = (int(bl[0]), int(bl[1]))
	pts = np.array([tl, tr, br, bl],np.int32)
	# pts = pts.reshape((-1, 1, 2))
	print(f'pts: {pts}')
    # endregion

	# region Read image
	image_input_file="D:/Master/OCR_Nom/fulllow_ocr_temple/input/cau_doi_1.jpg"
	im = Image.open(image_input_file).convert("RGB")
	pil_image = np.asarray(im)
	# endregion

	# region Crop polygon image
	polygon_img = _polygon_crop(
        img_array= pil_image,
        polygon= pts
	)
	pil_polygon_img = Image.fromarray(polygon_img)
	pil_polygon_img.save('polygon.png')
	# endregion
