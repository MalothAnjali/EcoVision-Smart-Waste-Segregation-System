import { X, Recycle, Trash2, AlertTriangle, Leaf, Info } from 'lucide-react'

const ClassInfo = ({ classes, onClose }) => {
  const getIcon = (className) => {
    const icons = {
      'Recyclable': Recycle,
      'Non-Recyclable': Trash2,
      'Hazardous': AlertTriangle,
      'Organic': Leaf
    }
    return icons[className] || Info
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white">Waste Categories</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-slate-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 grid md:grid-cols-2 gap-6">
          {classes.map((classItem) => {
            const Icon = getIcon(classItem.name)
            return (
              <div
                key={classItem.id}
                className="bg-slate-900/50 rounded-lg border p-6 hover:border-slate-600 transition-all"
                style={{ borderColor: `${classItem.color}30` }}
              >
                <div className="flex items-start gap-4">
                  <div
                    className="p-3 rounded-lg"
                    style={{ backgroundColor: `${classItem.color}20` }}
                  >
                    <Icon
                      className="w-8 h-8"
                      style={{ color: classItem.color }}
                    />
                  </div>
                  
                  <div className="flex-1">
                    <h3 
                      className="text-xl font-bold mb-2"
                      style={{ color: classItem.color }}
                    >
                      {classItem.name}
                    </h3>
                    <p className="text-slate-400 text-sm leading-relaxed">
                      {classItem.description}
                    </p>
                    
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-slate-300 mb-2">Examples:</h4>
                      <ul className="text-sm text-slate-400 space-y-1">
                        {getExamples(classItem.name).map((example, idx) => (
                          <li key={idx}>• {example}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-700 p-6 bg-slate-900/50">
          <div className="text-center text-slate-400 text-sm">
            <p>Proper waste segregation helps protect our environment and enables effective recycling.</p>
            <p className="mt-2">Always check local guidelines for specific disposal requirements.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

const getExamples = (className) => {
  const examples = {
    'Recyclable': [
      'Plastic bottles and containers',
      'Paper, cardboard, and newspapers',
      'Metal cans (aluminum, steel)',
      'Glass bottles and jars',
      'Clean packaging materials'
    ],
    'Non-Recyclable': [
      'Contaminated packaging',
      'Mixed material items',
      'Wrappers and chips packets',
      'Styrofoam products',
      'Broken ceramics'
    ],
    'Hazardous': [
      'Batteries (all types)',
      'Paint cans and chemicals',
      'Pesticides and herbicides',
      'Electronic waste',
      'Medical waste'
    ],
    'Organic': [
      'Food scraps and leftovers',
      'Fruit and vegetable peels',
      'Yard waste (leaves, grass)',
      'Coffee grounds and tea bags',
      'Compostable materials'
    ]
  }
  return examples[className] || []
}

export default ClassInfo