import { Link } from 'react-router-dom'
import { ScanLine, Zap, TrendingUp, Trash2, Recycle, AlertTriangle, Leaf } from 'lucide-react'
import { getDetectionStats } from '../utils/storage'
import { useEffect, useState } from 'react'

const Dashboard = () => {
  const [stats, setStats] = useState({
    total: 0,
    recyclable: 0,
    nonRecyclable: 0,
    hazardous: 0,
    organic: 0
  })

  useEffect(() => {
    setStats(getDetectionStats())
  }, [])

  const features = [
    {
      title: 'Classify Waste',
      description: 'Upload images or use camera to classify waste items',
      icon: ScanLine,
      color: 'bg-blue-500',
      link: '/classify'
    },
    {
      title: 'Live Detection',
      description: 'Continuous real-time automatic classification',
      icon: Zap,
      color: 'bg-gradient-to-br from-green-500 to-emerald-600',
      link: '/live-detection'
    }
  ]

  const statCards = [
    { label: 'Total Scans', value: stats.total, icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Recyclable', value: stats.recyclable, icon: Recycle, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Non-Recyclable', value: stats.nonRecyclable, icon: Trash2, color: 'text-red-600', bg: 'bg-red-50' },
    { label: 'Hazardous', value: stats.hazardous, icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50' },
    { label: 'Organic', value: stats.organic, icon: Leaf, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  ]

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome to EcoVision</h1>
        <p className="text-gray-600">Smart waste classification for a cleaner environment</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
              <div className={`w-12 h-12 ${stat.bg} rounded-lg flex items-center justify-center mb-4`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <p className="text-2xl font-bold text-gray-800 mb-1">{stat.value}</p>
              <p className="text-sm text-gray-600">{stat.label}</p>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Link
                key={index}
                to={feature.link}
                className="bg-white rounded-xl p-8 border border-gray-200 hover:shadow-xl hover:border-primary-300 transition-all group"
              >
                <div className={`w-16 h-16 ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </Link>
            )
          })}
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-8 text-white">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">Making a Difference</h3>
            <p className="text-green-50 mb-4">
              Every waste item classified correctly helps reduce environmental pollution and promotes better recycling practices.
            </p>
            <Link 
              to="/history"
              className="inline-block bg-white text-green-600 px-6 py-2 rounded-lg font-medium hover:bg-green-50 transition-colors"
            >
              View Past Detections
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard