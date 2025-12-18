import { useState, useRef, useEffect } from 'react'
import Webcam from 'react-webcam'
import { Camera, Zap, Loader2, Info, Play, Pause } from 'lucide-react'
import { classifyImage } from '../services/api'

const LiveDetection = () => {
  const [isScanning, setIsScanning] = useState(false)
  const [currentResult, setCurrentResult] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [scanCount, setScanCount] = useState(0)
  
  const webcamRef = useRef(null)
  const intervalRef = useRef(null)

  // Start/Stop continuous scanning
  useEffect(() => {
    if (isScanning) {
      // Scan every 2.5 seconds
      intervalRef.current = setInterval(() => {
        captureAndClassify()
      }, 2500)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isScanning])

  const captureAndClassify = async () => {
    if (!webcamRef.current || isProcessing) return

    const imageSrc = webcamRef.current.getScreenshot()
    if (!imageSrc) return

    setIsProcessing(true)
    setError(null)

    try {
      // Convert to blob
      const response = await fetch(imageSrc)
      const blob = await response.blob()
      const file = new File([blob], 'live-capture.jpg', { type: 'image/jpeg' })

      // Classify
      const data = await classifyImage(file)
      setCurrentResult(data)
      setScanCount(prev => prev + 1)

      // Note: Live detection results are NOT saved to history
      // Only manual captures (from Classify page) are saved
    } catch (err) {
      setError(err.message || 'Classification failed')
      setIsScanning(false) // Stop on error
    } finally {
      setIsProcessing(false)
    }
  }

  const toggleScanning = () => {
    setIsScanning(!isScanning)
    if (!isScanning) {
      setScanCount(0)
      setCurrentResult(null)
      setError(null)
    }
  }

  const getColorForClass = (className) => {
    const colors = {
      'Recyclable': { bg: 'bg-green-500', text: 'text-green-500', border: 'border-green-500' },
      'Non-Recyclable': { bg: 'bg-red-500', text: 'text-red-500', border: 'border-red-500' },
      'Hazardous': { bg: 'bg-yellow-500', text: 'text-yellow-500', border: 'border-yellow-500' },
      'Organic': { bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500' }
    }
    return colors[className] || colors['Recyclable']
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Live Detection</h1>
            <p className="text-gray-600">Continuous real-time waste classification</p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Camera Feed - Takes 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-lg">
            {/* Camera Container */}
            <div className="relative bg-black">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                className="w-full rounded-lg"
                videoConstraints={{
                  width: 1280,
                  height: 720,
                  facingMode: "environment"
                }}
              />

              {/* Colored Detection Border */}
              {currentResult && isScanning && (
                <div className="absolute inset-0 pointer-events-none">
                  <div className="absolute inset-2 border-8 rounded-lg shadow-2xl transition-all duration-300" 
                    style={{ borderColor: currentResult.prediction?.color || '#22c55e' }} />
                </div>
              )}

              {/* Scanning Overlay */}
              {isScanning && (
                <div className="absolute inset-0 pointer-events-none">
                  {/* Scanning border animation */}
                  <div className={`absolute inset-4 border-4 rounded-lg ${currentResult ? 'border-transparent' : 'border-green-500 animate-pulse'}`} />
                  
                  {/* Corner markers */}
                  <div className="absolute top-8 left-8 w-12 h-12 border-t-4 border-l-4 border-green-500" />
                  <div className="absolute top-8 right-8 w-12 h-12 border-t-4 border-r-4 border-green-500" />
                  <div className="absolute bottom-8 left-8 w-12 h-12 border-b-4 border-l-4 border-green-500" />
                  <div className="absolute bottom-8 right-8 w-12 h-12 border-b-4 border-r-4 border-green-500" />

                  {/* Processing indicator */}
                  {isProcessing && (
                    <div className="absolute top-4 right-4 bg-green-500/90 backdrop-blur-sm px-4 py-2 rounded-full flex items-center gap-2">
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                      <span className="text-white font-medium">Analyzing...</span>
                    </div>
                  )}

                  {/* Scan count */}
                  <div className="absolute top-4 left-4 bg-black/70 backdrop-blur-sm px-4 py-2 rounded-full">
                    <span className="text-white font-medium">Scans: {scanCount}</span>
                  </div>
                </div>
              )}

              {/* Result Overlay */}
              {currentResult && isScanning && (
                <div className="absolute bottom-4 left-4 right-4">
                  <div className={`bg-white/95 backdrop-blur-sm rounded-xl border-2 p-4 shadow-2xl ${getColorForClass(currentResult.prediction?.class).border}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 ${getColorForClass(currentResult.prediction?.class).bg} rounded-lg flex items-center justify-center`}>
                          <span className="text-2xl text-white font-bold">
                            {currentResult.prediction?.class?.[0]}
                          </span>
                        </div>
                        <div>
                          <h3 className={`text-xl font-bold ${getColorForClass(currentResult.prediction?.class).text}`}>
                            {currentResult.prediction?.class}
                          </h3>
                          <p className="text-sm text-gray-600">
                            Confidence: {(currentResult.prediction?.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      <div className="w-16 h-16">
                        <svg className="transform -rotate-90" viewBox="0 0 36 36">
                          <path
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="#e5e7eb"
                            strokeWidth="3"
                          />
                          <path
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke={currentResult.prediction?.color}
                            strokeWidth="3"
                            strokeDasharray={`${currentResult.prediction?.confidence * 100}, 100`}
                          />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="p-6 bg-gray-50">
              <div className="flex items-center gap-4">
                <button
                  onClick={toggleScanning}
                  className={`flex-1 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 shadow-lg ${
                    isScanning
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white'
                  }`}
                >
                  {isScanning ? (
                    <>
                      <Pause className="w-6 h-6" />
                      Stop Live Detection
                    </>
                  ) : (
                    <>
                      <Play className="w-6 h-6" />
                      Start Live Detection
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Info Card */}
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-xl p-6">
            <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <Info className="w-5 h-5" />
              How Live Detection Works
            </h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>• Point your camera at a waste item</li>
              <li>• Click "Start Live Detection"</li>
              <li>• Results update automatically every 2-3 seconds</li>
              <li>• All detections are saved to history</li>
              <li>• Green border means actively scanning</li>
            </ul>
          </div>
        </div>

        {/* Sidebar - Recent Results */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Current Session</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Total Scans</span>
                <span className="text-2xl font-bold text-gray-800">{scanCount}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Status</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  isScanning ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-700'
                }`}>
                  {isScanning ? '● LIVE' : '○ Stopped'}
                </span>
              </div>

              {currentResult && (
                <div className="mt-4 p-4 border border-gray-200 rounded-lg">
                  <p className="text-xs text-gray-500 mb-2">Latest Detection</p>
                  <h4 className={`text-lg font-bold ${getColorForClass(currentResult.prediction?.class).text}`}>
                    {currentResult.prediction?.class}
                  </h4>
                  <div className="mt-2 space-y-1">
                    {currentResult.all_predictions?.slice(0, 3).map((pred, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">{pred.class}</span>
                        <span className="text-gray-800 font-medium">
                          {(pred.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Tips */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
            <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Pro Tips
            </h3>
            <ul className="space-y-2 text-sm text-green-800">
              <li>• Hold camera steady for best results</li>
              <li>• Keep item centered in frame</li>
              <li>• Ensure good lighting</li>
              <li>• One item at a time works best</li>
              <li>• Results update every 2-3 seconds</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LiveDetection