import { useState, useEffect } from 'react';
import { AnimatePresence } from 'motion/react';
import { Toaster, toast } from 'sonner';
import { UploadAndConfigure } from './components/UploadAndConfigure';
import { GenerationProgress } from './components/GenerationProgress';
import { GenerationResult } from './components/GenerationResult';
import { Explanation } from './components/Explanation';
import { History } from './components/History';

type Screen = 'upload' | 'progress' | 'result' | 'explanation' | 'history';

// Types matching Backend API
interface AnalysisData {
  stats: any;
  planar_hints_count: number;
  cylindrical_hints_count: number;
}

interface GenerationData {
  download_url: string;
  explanation: string;
  status?: string;
}

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

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('upload');
  const [records, setRecords] = useState<ConversionRecord[]>([]);
  const [_selectedRecordId, setSelectedRecordId] = useState<string | null>(null);

  // API State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [generationData, setGenerationData] = useState<GenerationData | null>(null);

  const API_BASE = "http://localhost:8000";

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/history`);
      if (res.ok) {
        const data = await res.json();
        setRecords(data);
      }
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  // Fetch history on mount and when entering history screen
  useEffect(() => {
    fetchHistory();
  }, [currentScreen]);

  const handleViewDetails = async (recordId: string) => {
    try {
      // Show loading or toast?
      const res = await fetch(`${API_BASE}/api/session/${recordId}`);
      if (res.ok) {
        const data = await res.json();
        setAnalysisData(data.analysis);
        setGenerationData(data.generation);
        setSelectedRecordId(recordId);
        setCurrentScreen('result');
      } else {
        toast.error("Could not load details for this session.");
      }
    } catch (e) {
      toast.error("Failed to fetch session details.");
    }
  };

  const handleBackToHome = () => {
    setCurrentScreen('upload');
    setSelectedRecordId(null);
    setSessionId(null);
    setAnalysisData(null);
    setGenerationData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100">
      <Toaster position="top-center" richColors />

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-gray-900 text-center">
            STL to STEP Conversion Assistant
          </h1>
          <p className="text-center text-gray-600 mt-2">
            AI-powered engineering tool for geometric feature extraction
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {currentScreen === 'upload' && (
            <UploadAndConfigure
              key="upload"
              apiBase={API_BASE}
              onAnalysisComplete={(sid, data) => {
                setSessionId(sid);
                setAnalysisData(data);
              }}
              onGenerate={() => setCurrentScreen('progress')}
              onViewHistory={() => setCurrentScreen('history')}
              analysisData={analysisData}
            />
          )}

          {currentScreen === 'progress' && sessionId && (
            <GenerationProgress
              key="progress"
              apiBase={API_BASE}
              sessionId={sessionId}
              onComplete={(data) => {
                setGenerationData(data);
                setCurrentScreen('result');
                if (data.status === 'Fallback') {
                  toast.warning("API Call Failed", {
                    description: "Switched to Smart Geometric Extraction mode."
                  });
                } else {
                  toast.success("API Call Successful", {
                    description: "Conversion completed using AI strategy."
                  });
                }
              }}
            />
          )}

          {currentScreen === 'result' && generationData && (
            <GenerationResult
              key="result"
              apiBase={API_BASE}
              data={generationData}
              analysisData={analysisData}
              onViewExplanation={() => setCurrentScreen('explanation')}
              onBackToHome={handleBackToHome}
            />
          )}

          {currentScreen === 'explanation' && generationData && (
            <Explanation
              key="explanation"
              explanationMarkdown={generationData.explanation}
              onBack={() => setCurrentScreen('result')}
              onBackToHome={handleBackToHome}
            />
          )}

          {currentScreen === 'history' && (
            <History
              key="history"
              onBack={handleBackToHome}
              records={records}
              onViewDetails={handleViewDetails}
              apiBase={API_BASE}
            />
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="mt-20 pb-8 text-center text-sm text-gray-500">
        <p>Engineering Course Project • High-Fidelity Prototype</p>
      </footer>
    </div>
  );
}
