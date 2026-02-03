import { Download, FileText, CircleCheck, Home } from 'lucide-react';
import { motion } from 'motion/react';
import { useState } from 'react';

interface GenerationResultProps {
  onViewExplanation: () => void;
  onBackToHome: () => void;
  apiBase: string;
  data: {
    download_url: string;
    explanation: string;
  };
  analysisData: any;
}

export function GenerationResult({ onViewExplanation, onBackToHome, apiBase, data, analysisData }: GenerationResultProps) {
  const [downloaded, setDownloaded] = useState(false);

  const handleDownload = () => {
    setDownloaded(true);
    // Real download
    const fullUrl = `${apiBase}${data.download_url}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = 'converted.step'; // The browser might use the server filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => setDownloaded(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto space-y-8"
    >
      {/* Success Indicator */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.2 }}
        className="flex justify-center"
      >
        <div className="relative">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 2, repeat: 2 }}
            className="absolute inset-0 bg-green-400 rounded-full blur-xl"
          />
          <CircleCheck className="text-green-600 relative" size={80} strokeWidth={2} />
        </div>
      </motion.div>

      <div className="text-center">
        <h2 className="mb-2 text-gray-900">STEP Generation Complete!</h2>
        <p className="text-gray-600">Your STEP file has been successfully generated</p>
      </div>

      {/* Download Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <motion.button
          onClick={handleDownload}
          whileHover={{ scale: 1.02, boxShadow: '0 10px 25px rgba(59, 130, 246, 0.3)' }}
          whileTap={{ scale: 0.98 }}
          className="w-full bg-blue-600 text-white py-4 px-8 rounded-lg shadow-md hover:bg-blue-700 transition-colors flex items-center justify-center space-x-3"
        >
          <Download size={24} />
          <span>{downloaded ? '✓ Download Started' : 'Download STEP file'}</span>
        </motion.button>
      </motion.div>

      {/* Summary Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-8"
      >
        <h3 className="mb-6 text-gray-900">Generation Summary</h3>

        <div className="space-y-6">
          {/* Detected Features */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-1 h-6 bg-blue-500 rounded-full" />
              <h4 className="text-gray-900">Detected Features</h4>
            </div>
            <div className="ml-4 space-y-2">
              <motion.div
                whileHover={{ x: 4 }}
                className="flex items-center justify-between p-3 rounded-lg bg-blue-50 border border-blue-100"
              >
                <span className="text-gray-700">Planar Surfaces</span>
                <span className="text-blue-700 px-3 py-1 bg-blue-100 rounded-full text-sm">{analysisData?.planar_hints_count || 0} detected</span>
              </motion.div>
              <motion.div
                whileHover={{ x: 4 }}
                className="flex items-center justify-between p-3 rounded-lg bg-purple-50 border border-purple-100"
              >
                <span className="text-gray-700">Cylindrical Features</span>
                <span className="text-purple-700 px-3 py-1 bg-purple-100 rounded-full text-sm">{analysisData?.cylindrical_hints_count || 0} detected</span>
              </motion.div>
              <motion.div
                whileHover={{ x: 4 }}
                className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-100"
              >
                <span className="text-gray-700">Mesh Triangles</span>
                <span className="text-green-700 px-3 py-1 bg-green-100 rounded-full text-sm">{analysisData?.stats?.num_faces?.toLocaleString() || 0} faces</span>
              </motion.div>
            </div>
          </div>

          {/* Physical Properties */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-1 h-6 bg-teal-500 rounded-full" />
              <h4 className="text-gray-900">Physical Properties</h4>
            </div>
            <div className="ml-4 space-y-2">
              <div className="grid grid-cols-2 gap-4">
                <motion.div
                  whileHover={{ x: 4 }}
                  className="p-3 rounded-lg bg-indigo-50 border border-indigo-100"
                >
                  <div className="text-xs text-gray-500 uppercase tracking-wide">Volume</div>
                  <div className="text-gray-900 font-bold">
                    {analysisData?.stats?.volume ? analysisData.stats.volume.toFixed(2) : 'N/A'} <span className="text-xs font-normal">mm³</span>
                  </div>
                </motion.div>

                <motion.div
                  whileHover={{ x: 4 }}
                  className="p-3 rounded-lg bg-teal-50 border border-teal-100"
                >
                  <div className="text-xs text-gray-500 uppercase tracking-wide">Surface Area</div>
                  <div className="text-gray-900 font-bold">
                    {analysisData?.stats?.surface_area ? analysisData.stats.surface_area.toFixed(2) : 'N/A'} <span className="text-xs font-normal">mm²</span>
                  </div>
                </motion.div>
              </div>

              <motion.div
                whileHover={{ x: 4 }}
                className="p-3 rounded-lg bg-amber-50 border border-amber-100"
              >
                <div className="text-xs text-gray-500 uppercase tracking-wide">Center of Mass</div>
                <div className="text-gray-900 font-mono text-sm">
                  {analysisData?.stats?.center_mass?.map((c: number) => c.toFixed(2)).join(', ') || 'N/A'}
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* View Explanation Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <motion.button
          onClick={onViewExplanation}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="w-full bg-white text-blue-600 py-4 px-8 rounded-lg shadow-sm border-2 border-blue-600 hover:bg-blue-50 transition-colors flex items-center justify-center space-x-3"
        >
          <FileText size={24} />
          <span>View Detailed Explanation</span>
        </motion.button>
      </motion.div>

      {/* Back to Home Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <motion.button
          onClick={onBackToHome}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="w-full bg-gray-100 text-gray-700 py-3 px-8 rounded-lg shadow-sm hover:bg-gray-200 transition-colors flex items-center justify-center space-x-3"
        >
          <Home size={20} />
          <span>Back to Home</span>
        </motion.button>
      </motion.div>
    </motion.div>
  );
}