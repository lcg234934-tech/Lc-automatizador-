import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity, 
  Target,
  Play,
  Pause,
  Settings,
  Zap,
  Coins
} from 'lucide-react'
import { Link } from 'react-router-dom'

const API_BASE_URL = 'http://localhost:5000/api'

export default function Dashboard({ user }) {
  const [stats, setStats] = useState({
    daily: { profit: 0, bets: 0 },
    weekly: { profit: 0, bets: 0 },
    monthly: { profit: 0, bets: 0 }
  })
  const [strategies, setStrategies] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [user.id])

  const fetchDashboardData = async () => {
    try {
      // Fetch strategies
      const strategiesResponse = await fetch(`${API_BASE_URL}/strategies?user_id=${user.id}`)
      const strategiesData = await strategiesResponse.json()
      
      // Fetch stats for different periods
      const [dailyStats, weeklyStats, monthlyStats] = await Promise.all([
        fetch(`${API_BASE_URL}/bets/stats?user_id=${user.id}&period=day`).then(r => r.json()),
        fetch(`${API_BASE_URL}/bets/stats?user_id=${user.id}&period=week`).then(r => r.json()),
        fetch(`${API_BASE_URL}/bets/stats?user_id=${user.id}&period=month`).then(r => r.json())
      ])

      setStrategies(strategiesData)
      setStats({
        daily: dailyStats,
        weekly: weeklyStats,
        monthly: monthlyStats
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleStrategy = async (strategyId, currentStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/strategies/${strategyId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        // Update local state
        setStrategies(strategies.map(strategy => 
          strategy.id === strategyId 
            ? { ...strategy, is_active: !currentStatus }
            : strategy
        ))
      }
    } catch (error) {
      console.error('Error toggling strategy:', error)
    }
  }

  const getStrategyDisplayName = (strategyType) => {
    switch (strategyType) {
      case 'terminal_8':
        return 'Terminal 8 (1→6)'
      case '3x3_pattern':
        return 'Padrão 3x3'
      case '2x7_pattern':
        return 'Padrão 2x7'
      default:
        return strategyType
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="roulette-wheel w-32 h-32"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="roulette-wheel w-16 h-16 mr-4">
            <div className="absolute inset-0 flex items-center justify-center">
              <Zap className="h-8 w-8 text-white z-10" />
            </div>
          </div>
          <h1 className="text-4xl font-bold gold-text">Dashboard</h1>
        </div>
        <p className="text-muted-foreground text-lg">Bem-vindo de volta, <span className="gold-text font-semibold">{user.username}</span>!</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="roulette-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium gold-text">Lucro Diário</CardTitle>
            <div className="casino-chip w-8 h-8">
              <DollarSign className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              R$ {stats.daily.total_profit?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.daily.total_bets || 0} apostas hoje
            </p>
          </CardContent>
        </Card>

        <Card className="roulette-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium gold-text">Lucro Semanal</CardTitle>
            <div className="casino-chip w-8 h-8 green">
              <TrendingUp className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              R$ {stats.weekly.total_profit?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.weekly.total_bets || 0} apostas esta semana
            </p>
          </CardContent>
        </Card>

        <Card className="roulette-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium gold-text">Lucro Mensal</CardTitle>
            <div className="casino-chip w-8 h-8">
              <Activity className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              R$ {stats.monthly.total_profit?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.monthly.total_bets || 0} apostas este mês
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Strategies Control */}
      <Card className="roulette-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="gold-text">Controle de Estratégias</CardTitle>
              <CardDescription className="text-muted-foreground">
                Ative ou desative suas estratégias de apostas
              </CardDescription>
            </div>
            <Link to="/strategies">
              <Button className="roulette-button" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Configurar
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {strategies.length === 0 ? (
            <div className="text-center py-8">
              <div className="roulette-wheel w-24 h-24 mx-auto mb-4">
                <div className="absolute inset-0 flex items-center justify-center">
                  <Target className="h-12 w-12 text-white z-10" />
                </div>
              </div>
              <h3 className="text-lg font-medium text-foreground mb-2">
                Nenhuma estratégia configurada
              </h3>
              <p className="text-muted-foreground mb-4">
                Configure suas estratégias de apostas para começar
              </p>
              <Link to="/strategies">
                <Button className="roulette-button">Configurar Estratégias</Button>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {strategies.map((strategy) => (
                <div
                  key={strategy.id}
                  className="roulette-card p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground">{strategy.name}</h4>
                    <Badge variant={strategy.is_active ? "default" : "secondary"} className={strategy.is_active ? "bg-primary text-primary-foreground" : ""}>
                      {strategy.is_active ? "Ativa" : "Inativa"}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-muted-foreground">
                    {getStrategyDisplayName(strategy.strategy_type)}
                  </p>
                  
                  <Button
                    onClick={() => toggleStrategy(strategy.id, strategy.is_active)}
                    className={`w-full ${strategy.is_active ? 'roulette-button' : 'roulette-button green'}`}
                    size="sm"
                  >
                    {strategy.is_active ? (
                      <>
                        <Pause className="h-4 w-4 mr-2" />
                        Pausar
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Ativar
                      </>
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="roulette-card">
          <CardHeader>
            <CardTitle className="gold-text">Ações Rápidas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/strategies" className="block">
              <Button className="roulette-button w-full justify-start">
                <Settings className="h-4 w-4 mr-2" />
                Configurar Estratégias
              </Button>
            </Link>
            <Link to="/reports" className="block">
              <Button className="roulette-button green w-full justify-start">
                <TrendingUp className="h-4 w-4 mr-2" />
                Ver Relatórios
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="roulette-card">
          <CardHeader>
            <CardTitle className="gold-text">Status do Sistema</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Conexão API</span>
                <Badge className="bg-primary text-primary-foreground">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Estratégias Ativas</span>
                <div className="casino-chip w-6 h-6 text-xs">
                  {strategies.filter(s => s.is_active).length}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Última Atualização</span>
                <span className="text-sm text-foreground">
                  {new Date().toLocaleTimeString('pt-BR')}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

