import { CheckCircle, TrendingUp } from 'lucide-react'

const ResultCard = ({ result, getIcon }) => {
  if (!result || !result.prediction) return null

  const { prediction, all_predictions } = result
  const Icon = getIcon(prediction.class)

  return (
    <div className="space-y-6">
      {/* Main Result */}
      <div className="bg-white rounded-xl border-2 p-6 shadow-lg transition-all hover:shadow-xl"
        style={{ borderColor: prediction.color }}
      >
        <div className="flex items-start gap-4">
          <div className="p-4 rounded-xl"
            style={{ backgroundColor: `${prediction.color}20` }}
          >
            <Icon className="w-10 h-10" style={{ color: prediction.color }} />
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <h3 className="text-2xl font-bold text-gray-800">
                {prediction.class}
              </h3>
              <CheckCircle className="w-6 h-6" style={{ color: prediction.color }} />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 font-medium">Confidence</span>
                <span className="text-gray-800 font-bold">
                  {(prediction.confidence * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${prediction.confidence * 100}%`,
                    backgroundColor: prediction.color
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="mt-4 p-4 rounded-lg border"
          style={{ 
            backgroundColor: `${prediction.color}10`,
            borderColor: `${prediction.color}30`
          }}
        >
          <p className="text-sm text-gray-700 leading-relaxed">
            {getRecommendation(prediction.class)}
          </p>
        </div>
      </div>

      {/* All Predictions */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-gray-600" />
          <h4 className="text-lg font-semibold text-gray-800">All Predictions</h4>
        </div>
        
        <div className="space-y-3">
          {all_predictions.map((pred, idx) => {
            const PredIcon = getIcon(pred.class)
            return (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <PredIcon className="w-4 h-4" style={{ color: pred.color }} />
                    <span className="text-gray-700 text-sm font-medium">{pred.class}</span>
                  </div>
                  <span className="text-gray-600 text-sm font-semibold">
                    {(pred.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${pred.confidence * 100}%`,
                      backgroundColor: pred.color
                    }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

const getRecommendation = (className) => {
  const recommendations = {
    'Recyclable': '♻️ Great! This item can be recycled. Please clean it and place it in the recyclable bin. Items like plastic bottles, paper, and metal cans help reduce environmental waste.',
    'Non-Recyclable': '🗑️ This item cannot be recycled. Dispose of it in the general waste bin. Consider reducing usage of such items when possible.',
    'Hazardous': '⚠️ CAUTION! This is hazardous waste. Do not dispose of it in regular bins. Contact your local hazardous waste disposal facility for proper handling.',
    'Organic': '🌱 This is organic waste. Consider composting it if possible, or dispose of it in the organic waste bin. It helps create nutrient-rich soil!'
  }
  return recommendations[className] || 'Please dispose of this item properly.'
}

export default ResultCard