import { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { X, Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

const NOTIFICATION_TYPES = {
  info: { icon: Info, className: 'border-blue-200 bg-blue-50 text-blue-800' },
  success: { icon: CheckCircle, className: 'border-green-200 bg-green-50 text-green-800' },
  warning: { icon: AlertTriangle, className: 'border-yellow-200 bg-yellow-50 text-yellow-800' },
  error: { icon: XCircle, className: 'border-red-200 bg-red-50 text-red-800' }
}

export default function Notifications() {
  const [notifications, setNotifications] = useState([])

  // Function to add a new notification
  const addNotification = (type, message, autoClose = true) => {
    const id = Date.now()
    const newNotification = {
      id,
      type,
      message,
      timestamp: new Date()
    }
    
    setNotifications(prev => [...prev, newNotification])
    
    if (autoClose) {
      setTimeout(() => {
        removeNotification(id)
      }, 5000) // Auto-remove after 5 seconds
    }
  }

  // Function to remove a notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  // Expose addNotification globally for use in other components
  useEffect(() => {
    window.addNotification = addNotification
    return () => {
      delete window.addNotification
    }
  }, [])

  if (notifications.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => {
        const { icon: Icon, className } = NOTIFICATION_TYPES[notification.type]
        
        return (
          <Alert key={notification.id} className={`${className} shadow-lg`}>
            <Icon className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span className="flex-1 mr-2">{notification.message}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeNotification(notification.id)}
                className="h-6 w-6 p-0 hover:bg-transparent"
              >
                <X className="h-3 w-3" />
              </Button>
            </AlertDescription>
          </Alert>
        )
      })}
    </div>
  )
}

// Utility functions for easy notification usage
export const notify = {
  info: (message) => window.addNotification?.('info', message),
  success: (message) => window.addNotification?.('success', message),
  warning: (message) => window.addNotification?.('warning', message),
  error: (message) => window.addNotification?.('error', message)
}

