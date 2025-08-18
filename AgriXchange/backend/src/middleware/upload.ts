import multer from 'multer';
import path from 'path';

// Memory storage for now (can be enhanced later with Cloudinary)
const storage = multer.memoryStorage();

// File filter
const fileFilter = (req: any, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  if (file.mimetype.startsWith('image/')) {
    cb(null, true);
  } else {
    cb(new Error('Only image files are allowed!'));
  }
};

// Create multer instance
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
    files: 5, // Max 5 files
  },
});

// Note: Cloudinary upload is handled in the controller after multer parses the files.

export const uploadProductImages = upload.array('images', 5);
