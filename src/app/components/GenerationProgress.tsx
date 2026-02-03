import { Loader } from 'lucide-react';
import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

interface GenerationProgressProps {
  onComplete: (data: any) => void;
  apiBase: string;
  sessionId: string;
}

const steps = [
  'Parsing STL',
  'Extracting geometric features',
  'Generating STEP representation'
];

export function GenerationProgress({ onComplete, apiBase, sessionId }: GenerationProgressProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [showViewResults, setShowViewResults] = useState(false);
  const [generationData, setGenerationData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    // Simulate initial steps while waiting for server
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => prev < 1 ? prev + 1 : prev);
    }, 1000);

    // Call API
    const generate = async () => {
      try {
        setCurrentStep(1); // Analysis done (backend re-uses it)
        const response = await fetch(`${apiBase}/api/generate/${sessionId}`, {
          method: 'POST'
        });

        if (!response.ok) throw new Error("Generation failed");

        const data = await response.json();

        if (mounted) {
          setGenerationData(data);
          setCurrentStep(2); // Done
          clearInterval(stepInterval);
          setTimeout(() => setShowViewResults(true), 500);
        }
      } catch (e) {
        console.error(e);
        if (mounted) setError("An error occurred during generation.");
      }
    };

    generate();

    return () => {
      mounted = false;
      clearInterval(stepInterval);
    };
  }, [apiBase, sessionId]);

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.4 }}
      className="max-w-2xl mx-auto"
    >
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-12">
        {/* Animated loader */}
        <div className="flex justify-center mb-8">
          {!showViewResults && !error ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Loader className="text-blue-600" size={64} />
            </motion.div>
          ) : error ? (
            <div className="text-red-500 text-4xl">⚠</div>
          ) : (
            <div className="text-green-500 text-6xl">✓</div>
          )}
        </div>

        <h2 className="text-center mb-2 text-gray-900">
          {error ? "Generation Failed" : showViewResults ? "Generation Complete" : "Generating STEP Model"}
        </h2>
        <p className="text-center text-gray-600 mb-8">
          {error ? error : showViewResults ? "Your file is ready." : "Please wait while we process your file..."}
        </p>

        {/* Progress bar */}
        {!error && (
          <div className="mb-8">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-blue-600 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
            <div className="text-center mt-2 text-sm text-gray-600">
              {Math.round(progress)}% Complete
            </div>
          </div>
        )}

        {/* Step indicators */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: -20 }}
              animate={{
                opacity: index <= currentStep ? 1 : 0.4,
                x: 0
              }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center space-x-4"
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all ${index < currentStep
                    ? 'bg-green-500 text-white'
                    : index === currentStep && !error
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
              >
                {index < currentStep ? (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 20 }}
                  >
                    ✓
                  </motion.span>
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>

              <div className="flex-1">
                <div className={`transition-colors ${index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                  {step}
                </div>
              </div>

              {index === currentStep && !showViewResults && !error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex-shrink-0"
                >
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <Loader className="text-blue-500" size={20} />
                  </motion.div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>

        {/* View Results Button */}
        {showViewResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mt-8"
          >
            <motion.button
              onClick={() => onComplete(generationData)}
              whileHover={{ scale: 1.02, boxShadow: '0 10px 25px rgba(34, 197, 94, 0.3)' }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-green-600 text-white py-4 px-8 rounded-lg shadow-md hover:bg-green-700 transition-colors"
            >
              View Results
            </motion.button>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
