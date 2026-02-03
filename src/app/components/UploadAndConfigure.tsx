import { Upload, Box, Activity, Grid3x3, History as HistoryIcon, Loader } from 'lucide-react';
import { motion } from 'motion/react';
import { useState } from 'react';

interface UploadAndConfigureProps {
  onGenerate: () => void;
  onViewHistory: () => void;
  apiBase: string;
  onAnalysisComplete: (sessionId: string, data: any) => void;
  analysisData: any;
}

export function UploadAndConfigure({
  onGenerate,
  onViewHistory,
  apiBase,
  onAnalysisComplete,
  analysisData
}: UploadAndConfigureProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [includeReport, setIncludeReport] = useState(true);
  const [generateFeatureBased, setGenerateFeatureBased] = useState(true);
  const [fileName, setFileName] = useState("");

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFile = async (file: File) => {
    try {
      setIsUploading(true);
      setFileName(file.name);

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${apiBase}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");

      const data = await response.json();
      onAnalysisComplete(data.session_id, data);
      setFileUploaded(true);

    } catch (e) {
      console.error(e);
      alert("Error uploading file");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto space-y-8"
    >
      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <h2 className="mb-6 text-gray-900">Upload STL File</h2>

        <motion.div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : fileUploaded
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100'
            }`}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <input
            type="file"
            accept=".stl"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />

          <motion.div
            initial={{ scale: 1 }}
            animate={{ scale: isDragging ? 1.1 : 1 }}
            transition={{ duration: 0.2 }}
          >
            {isUploading ? (
              <Loader className="mx-auto mb-4 text-blue-600 animate-spin" size={48} />
            ) : (
              <Upload className={`mx-auto mb-4 ${fileUploaded ? 'text-green-600' : 'text-gray-400'}`} size={48} />
            )}
          </motion.div>

          {isUploading ? (
            <div>
              <p className="text-blue-600 mb-2">Uploading & Analyzing...</p>
              <p className="text-gray-500 text-sm">Please wait</p>
            </div>
          ) : fileUploaded ? (
            <div>
              <p className="text-green-600 mb-2">✓ {fileName}</p>
              <p className="text-gray-500 text-sm">Click or drag to replace</p>
            </div>
          ) : (
            <div>
              <p className="text-gray-700 mb-2">Drag and drop your STL file here</p>
              <p className="text-gray-500 text-sm">or click to browse</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* STL Analysis Summary */}
      {analysisData && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.4 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-8"
        >
          <h2 className="mb-6 text-gray-900">STL Analysis Summary</h2>

          <div className="grid grid-cols-3 gap-6">
            <motion.div
              whileHover={{ y: -2 }}
              className="flex items-start space-x-3 p-4 rounded-lg bg-blue-50 border border-blue-100"
            >
              <Box className="text-blue-600 mt-1 flex-shrink-0" size={24} />
              <div>
                <div className="text-sm text-gray-600">Bounding Box</div>
                <div className="text-gray-900 font-medium">
                  {analysisData.stats.bbox_dimensions.map((d: number) => d.toFixed(1)).join(' × ')}
                  <span className="text-xs text-gray-500 ml-1">mm</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ y: -2 }}
              className="flex items-start space-x-3 p-4 rounded-lg bg-green-50 border border-green-100"
            >
              <Activity className="text-green-600 mt-1 flex-shrink-0" size={24} />
              <div>
                <div className="text-sm text-gray-600">Watertightness</div>
                <div className="text-gray-900 font-medium">
                  {analysisData.stats.is_watertight ? "✓ Manifold" : "⚠ Non-Manifold"}
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ y: -2 }}
              className="flex items-start space-x-3 p-4 rounded-lg bg-purple-50 border border-purple-100"
            >
              <Grid3x3 className="text-purple-600 mt-1 flex-shrink-0" size={24} />
              <div>
                <div className="text-sm text-gray-600">Mesh Triangles</div>
                <div className="text-gray-900 font-medium">{analysisData.stats.num_faces.toLocaleString()} tris</div>
              </div>
            </motion.div>

            {/* Row 2: Physical Properties */}
            <motion.div
              whileHover={{ y: -2 }}
              className="flex items-start space-x-3 p-4 rounded-lg bg-indigo-50 border border-indigo-100"
            >
              <div className="text-indigo-600 mt-1 flex-shrink-0 font-bold text-lg">V</div>
              <div>
                <div className="text-sm text-gray-600">Volume</div>
                <div className="text-gray-900 font-medium">
                  {analysisData.stats.volume ? analysisData.stats.volume.toFixed(2) : 'N/A'}
                  <span className="text-xs text-gray-500 ml-1">mm³</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ y: -2 }}
              className="flex items-start space-x-3 p-4 rounded-lg bg-teal-50 border border-teal-100"
            >
              <div className="text-teal-600 mt-1 flex-shrink-0 font-bold text-lg">A</div>
              <div>
                <div className="text-sm text-gray-600">Surface Area</div>
                <div className="text-gray-900 font-medium">
                  {analysisData.stats.surface_area ? analysisData.stats.surface_area.toFixed(2) : 'N/A'}
                  <span className="text-xs text-gray-500 ml-1">mm²</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ y: -2 }}
              className="flex items-start space-x-3 p-4 rounded-lg bg-amber-50 border border-amber-100"
            >
              <div className="text-amber-600 mt-1 flex-shrink-0 font-bold text-lg">CoM</div>
              <div>
                <div className="text-sm text-gray-600">Center of Mass</div>
                <div className="text-gray-900 font-medium text-xs">
                  {analysisData.stats.center_mass.map((c: number) => c.toFixed(1)).join(', ')}
                </div>
              </div>
            </motion.div>

          </div>

          <div className="mt-4 flex gap-4 text-sm text-gray-600">
            <span>Detected Planar Hints: <strong>{analysisData.planar_hints_count}</strong></span>
            <span>Detected Cylindrical Hints: <strong>{analysisData.cylindrical_hints_count}</strong></span>
          </div>
        </motion.div>
      )}

      {/* Configuration Options */}
      {fileUploaded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-8"
        >
          <h2 className="mb-6 text-gray-900">Configuration Options</h2>

          <div className="space-y-6">
            <motion.div
              whileHover={{ x: 2 }}
              className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-1">
                <div className="text-gray-900">Include explanation report</div>
                <div className="text-sm text-gray-600">Generate a detailed report of the conversion process</div>
              </div>
              <button
                onClick={() => setIncludeReport(!includeReport)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${includeReport ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
              >
                <motion.span
                  layout
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${includeReport ? 'translate-x-6' : 'translate-x-1'
                    }`}
                />
              </button>
            </motion.div>

            <motion.div
              whileHover={{ x: 2 }}
              className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-1">
                <div className="text-gray-900">Generate feature-based STEP (planes and cylinders)</div>
                <div className="text-sm text-gray-600">Extract geometric features for parametric modeling</div>
              </div>
              <button
                onClick={() => setGenerateFeatureBased(!generateFeatureBased)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${generateFeatureBased ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
              >
                <motion.span
                  layout
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${generateFeatureBased ? 'translate-x-6' : 'translate-x-1'
                    }`}
                />
              </button>
            </motion.div>
          </div>
        </motion.div>
      )}

      {/* Generate Button */}
      {fileUploaded && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <motion.button
            onClick={onGenerate}
            whileHover={{ scale: 1.02, boxShadow: '0 10px 25px rgba(59, 130, 246, 0.3)' }}
            whileTap={{ scale: 0.98 }}
            className="w-full bg-blue-600 text-white py-4 px-8 rounded-lg shadow-md hover:bg-blue-700 transition-colors"
          >
            Generate STEP
          </motion.button>
        </motion.div>
      )}

      {/* History Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
      >
        <motion.button
          onClick={onViewHistory}
          whileHover={{ scale: 1.02, boxShadow: '0 10px 25px rgba(107, 114, 128, 0.3)' }}
          whileTap={{ scale: 0.98 }}
          className="w-full bg-gray-600 text-white py-4 px-8 rounded-lg shadow-md hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2"
        >
          <HistoryIcon size={20} />
          <span>View Conversion History</span>
        </motion.button>
      </motion.div>
    </motion.div>
  );
}