import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Clock, 
  Calendar, 
  Settings, 
  Save,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import { notify } from './Notifications'

const API_BASE_URL = 'http://localhost:5000/api'

const DAYS_OF_WEEK = [
  { value: 1, label: 'Segunda', short: 'Seg' },
  { value: 2, label: 'Terça', short: 'Ter' },
  { value: 3, label: 'Quarta', short: 'Qua' },
  { value: 4, label: 'Quinta', short: 'Qui' },
  { value: 5, label: 'Sexta', short: 'Sex' },
  { value: 6, label: 'Sábado', short: 'Sáb' },
  { value: 7, label: 'Domingo', short: 'Dom' }
]

export default function ScheduleSettings({ strategy, onUpdate, onClose }) {
  const [scheduleData, setScheduleData] = useState({
    schedule_enabled: false,
    start_time: '',
    end_time: '',
    days_of_week: [],
    timezone: 'America/Sao_Paulo'
  })
  const [presets, setPresets] = useState({})
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (strategy) {
      setScheduleData({
        schedule_enabled: strategy.schedule_enabled || false,
        start_time: strategy.start_time || '',
        end_time: strategy.end_time || '',
        days_of_week: strategy.days_of_week || [],
        timezone: strategy.timezone || 'America/Sao_Paulo'
      })
    }
    loadPresets()
  }, [strategy])

  const loadPresets = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule/presets`)
      if (response.ok) {
        const presetsData = await response.json()
        setPresets(presetsData)
      }
    } catch (error) {
      console.error('Error loading presets:', error)
    }
  }

  const handleScheduleChange = (field, value) => {
    setScheduleData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleDayToggle = (dayValue) => {
    setScheduleData(prev => ({
      ...prev,
      days_of_week: prev.days_of_week.includes(dayValue)
        ? prev.days_of_week.filter(d => d !== dayValue)
        : [...prev.days_of_week, dayValue].sort()
    }))
  }

  const applyPreset = (presetKey) => {
    const preset = presets[presetKey]
    if (preset) {
      setScheduleData({
        schedule_enabled: preset.schedule_enabled,
        start_time: preset.start_time || '',
        end_time: preset.end_time || '',
        days_of_week: preset.days_of_week || [],
        timezone: preset.timezone || 'America/Sao_Paulo'
      })
      notify.success(`Preset "${preset.name}" aplicado`)
    }
  }

  const saveSchedule = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/strategies/${strategy.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(scheduleData)
      })

      if (response.ok) {
        const updatedStrategy = await response.json()
        notify.success('Agendamento salvo com sucesso!')
        if (onUpdate) {
          onUpdate(updatedStrategy)
        }
        if (onClose) {
          onClose()
        }
      } else {
        const error = await response.json()
        notify.error(`Erro ao salvar: ${error.error}`)
      }
    } catch (error) {
      notify.error(`Erro ao salvar: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const resetToDefault = () => {
    setScheduleData({
      schedule_enabled: false,
      start_time: '',
      end_time: '',
      days_of_week: [],
      timezone: 'America/Sao_Paulo'
    })
  }

  const getScheduleStatus = () => {
    if (!scheduleData.schedule_enabled) {
      return { status: 'always', text: 'Sempre ativo', color: 'bg-green-500' }
    }
    
    if (!scheduleData.start_time || !scheduleData.end_time || scheduleData.days_of_week.length === 0) {
      return { status: 'incomplete', text: 'Configuração incompleta', color: 'bg-yellow-500' }
    }
    
    return { status: 'scheduled', text: 'Agendado', color: 'bg-blue-500' }
  }

  const scheduleStatus = getScheduleStatus()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Agendamento de Estratégia</h2>
          <p className="text-gray-600">{strategy?.name}</p>
        </div>
        
        <Badge className={`${scheduleStatus.color} text-white`}>
          <Clock className="h-3 w-3 mr-1" />
          {scheduleStatus.text}
        </Badge>
      </div>

      {/* Main Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Configurações de Horário
          </CardTitle>
          <CardDescription>
            Configure quando esta estratégia deve estar ativa
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Enable Schedule */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="schedule_enabled" className="text-base font-medium">
                Habilitar Agendamento
              </Label>
              <p className="text-sm text-gray-600">
                Quando desabilitado, a estratégia ficará sempre ativa
              </p>
            </div>
            <Switch
              id="schedule_enabled"
              checked={scheduleData.schedule_enabled}
              onCheckedChange={(checked) => handleScheduleChange('schedule_enabled', checked)}
            />
          </div>

          {scheduleData.schedule_enabled && (
            <>
              {/* Time Range */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="start_time">Horário de Início</Label>
                  <Input
                    id="start_time"
                    type="time"
                    value={scheduleData.start_time}
                    onChange={(e) => handleScheduleChange('start_time', e.target.value)}
                  />
                </div>
                
                <div>
                  <Label htmlFor="end_time">Horário de Fim</Label>
                  <Input
                    id="end_time"
                    type="time"
                    value={scheduleData.end_time}
                    onChange={(e) => handleScheduleChange('end_time', e.target.value)}
                  />
                </div>
              </div>

              {/* Days of Week */}
              <div>
                <Label className="text-base font-medium mb-3 block">
                  Dias da Semana
                </Label>
                <div className="flex flex-wrap gap-2">
                  {DAYS_OF_WEEK.map((day) => (
                    <Button
                      key={day.value}
                      variant={scheduleData.days_of_week.includes(day.value) ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleDayToggle(day.value)}
                      className="min-w-[60px]"
                    >
                      {day.short}
                    </Button>
                  ))}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Selecione os dias em que a estratégia deve estar ativa
                </p>
              </div>

              {/* Timezone */}
              <div>
                <Label htmlFor="timezone">Fuso Horário</Label>
                <select
                  id="timezone"
                  value={scheduleData.timezone}
                  onChange={(e) => handleScheduleChange('timezone', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="America/Sao_Paulo">Brasília (GMT-3)</option>
                  <option value="America/New_York">Nova York (GMT-5)</option>
                  <option value="Europe/London">Londres (GMT+0)</option>
                  <option value="UTC">UTC (GMT+0)</option>
                </select>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Presets */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="h-5 w-5 mr-2" />
            Presets Rápidos
          </CardTitle>
          <CardDescription>
            Aplique configurações predefinidas comuns
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(presets).map(([key, preset]) => (
              <Button
                key={key}
                variant="outline"
                onClick={() => applyPreset(key)}
                className="h-auto p-3 text-left flex flex-col items-start"
              >
                <span className="font-medium">{preset.name}</span>
                <span className="text-xs text-gray-600 mt-1">{preset.description}</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Schedule Preview */}
      {scheduleData.schedule_enabled && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Info className="h-5 w-5 mr-2" />
              Resumo do Agendamento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-medium">{scheduleStatus.text}</span>
              </div>
              
              {scheduleData.start_time && scheduleData.end_time && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Horário:</span>
                  <span className="font-medium">
                    {scheduleData.start_time} às {scheduleData.end_time}
                  </span>
                </div>
              )}
              
              {scheduleData.days_of_week.length > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Dias:</span>
                  <span className="font-medium">
                    {scheduleData.days_of_week
                      .map(day => DAYS_OF_WEEK.find(d => d.value === day)?.short)
                      .join(', ')}
                  </span>
                </div>
              )}
              
              <div className="flex justify-between">
                <span className="text-gray-600">Fuso Horário:</span>
                <span className="font-medium">{scheduleData.timezone}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={resetToDefault}
          className="flex items-center"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Resetar
        </Button>
        
        <div className="flex space-x-2">
          {onClose && (
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
          )}
          
          <Button
            onClick={saveSchedule}
            disabled={isLoading}
            className="flex items-center"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Salvar Agendamento
          </Button>
        </div>
      </div>

      {/* Help */}
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          <strong>Dica:</strong> O agendamento permite que você controle automaticamente quando suas estratégias 
          devem estar ativas. Isso é útil para evitar apostas em horários específicos ou para focar em 
          períodos de maior atividade nas roletas.
        </AlertDescription>
      </Alert>
    </div>
  )
}

