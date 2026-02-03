import { ArrowLeft, Download, FileText, Calendar, Clock, CheckCircle, Box, Activity } from 'lucide-react';
import { motion } from 'motion/react';

interface ConversionRecord {
  id: string;
  fileName: string;
  date: string;
  time: string;
  status: 'success' | 'processing' | 'failed';
  planarSurfaces: number;
  cylindricalFeatures: number;
  edgeFeatures: number;
  fileSize: string;
}

interface HistoryProps {
  onBack: () => void;
  records: ConversionRecord[];
  onViewDetails: (recordId: string) => void;
  apiBase: string;
}

export function History({ onBack, records, onViewDetails, apiBase }: HistoryProps) {
  const handleDownload = (id: string, fileName: string) => {
    const fullUrl = `${apiBase}/api/download/${id}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = fileName; // Hint to browser
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-6xl mx-auto space-y-8"
    >
      {/* Back Button */}
      <motion.button
        onClick={onBack}
        whileHover={{ x: -4 }}
        whileTap={{ scale: 0.95 }}
        className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors"
      >
        <ArrowLeft size={20} />
        <span>Back to Home</span>
      </motion.button>

      {/* Title */}
      <div>
        <h2 className="mb-2 text-gray-900">Conversion History</h2>
        <p className="text-gray-600">View all your previous STL to STEP conversions</p>
      </div>

      {/* Records List */}
      <div className="space-y-4">
        {records.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center"
          >
            <Box className="mx-auto mb-4 text-gray-400" size={48} />
            <h3 className="text-gray-900 mb-2">No conversion history yet</h3>
            <p className="text-gray-600">Your conversion records will appear here</p>
          </motion.div>
        ) : (
          records.map((record, index) => (
            <motion.div
              key={record.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -2 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                {/* Left Section - File Info */}
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <div
                      className={`p-2 rounded-lg ${record.status === 'success'
                        ? 'bg-green-100'
                        : record.status === 'processing'
                          ? 'bg-blue-100'
                          : 'bg-red-100'
                        }`}
                    >
                      <CheckCircle
                        className={
                          record.status === 'success'
                            ? 'text-green-600'
                            : record.status === 'processing'
                              ? 'text-blue-600'
                              : 'text-red-600'
                        }
                        size={24}
                      />
                    </div>
                    <div>
                      <h3 className="text-gray-900">{record.fileName}</h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Calendar size={14} />
                          <span>{record.date}</span>
                        </div>
                        <div className="flex items-center space-x-1 text-sm text-gray-600">
                          <Clock size={14} />
                          <span>{record.time}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Features Summary */}
                  <div className="flex items-center space-x-6 ml-14">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full" />
                      <span className="text-sm text-gray-700">
                        {record.planarSurfaces} Planar
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full" />
                      <span className="text-sm text-gray-700">
                        {record.cylindricalFeatures} Cylindrical
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <span className="text-sm text-gray-700">
                        {record.edgeFeatures} Edges
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Activity size={14} className="text-gray-500" />
                      <span className="text-sm text-gray-600">{record.fileSize}</span>
                    </div>
                  </div>
                </div>

                {/* Right Section - Actions */}
                <div className="flex items-center space-x-3 ml-6">
                  <motion.button
                    onClick={() => onViewDetails(record.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center space-x-2"
                  >
                    <FileText size={18} />
                    <span>Details</span>
                  </motion.button>
                  <motion.button
                    onClick={() => handleDownload(record.id, record.fileName)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors flex items-center space-x-2"
                  >
                    <Download size={18} />
                    <span>Download</span>
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Statistics Card */}
      {records.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-8"
        >
          <h3 className="text-gray-900 mb-6">Statistics</h3>
          <div className="grid grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-gray-900 mb-1">{records.length}</div>
              <div className="text-sm text-gray-600">Total Conversions</div>
            </div>
            <div className="text-center">
              <div className="text-gray-900 mb-1">
                {records.filter(r => r.status === 'success').length}
              </div>
              <div className="text-sm text-gray-600">Successful</div>
            </div>
            <div className="text-center">
              <div className="text-gray-900 mb-1">
                {records.reduce((sum, r) => sum + r.planarSurfaces, 0)}
              </div>
              <div className="text-sm text-gray-600">Total Features</div>
            </div>
            <div className="text-center">
              <div className="text-gray-900 mb-1">100%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
