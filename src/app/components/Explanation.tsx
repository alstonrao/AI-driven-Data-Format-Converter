import { ArrowLeft, Home } from 'lucide-react';
import { motion } from 'motion/react';

interface ExplanationProps {
  onBack: () => void;
  onBackToHome: () => void;
  explanationMarkdown: string;
}

export function Explanation({ onBack, onBackToHome, explanationMarkdown }: ExplanationProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto space-y-8"
    >
      {/* Back Button */}
      <motion.button
        onClick={onBack}
        whileHover={{ x: -4 }}
        whileTap={{ scale: 0.95 }}
        className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors"
      >
        <ArrowLeft size={20} />
        <span>Back to Results</span>
      </motion.button>

      {/* Title */}
      <div>
        <h2 className="mb-2 text-gray-900">Explanation of STEP Generation</h2>
        <p className="text-gray-600">Detailed breakdown of the conversion process and detected features</p>
      </div>

      {/* Explanation Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-8"
      >
        <div className="prose prose-blue max-w-none">
          <pre className="whitespace-pre-wrap font-sans text-gray-700">
            {explanationMarkdown || "No explanation available."}
          </pre>
        </div>
      </motion.div>

      {/* Back to Home Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
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