import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  Calendar,
  BarChart3
} from 'lucide-react'

const API_BASE_URL = 'http://localhost:5000/api'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export default function Reports({ user }) {
  const [dailyData, setDailyData] = useState([])
  const [profitReport, setProfitReport] = useState(null)
  const [strategyPerformance, setStrategyPerformance] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState('month')

  useEffect(() => {
    fetchReportData()
  }, [user.id, selectedPeriod])

  const fetchReportData = async () => {
    setIsLoading(true)
    try {
      const [dailyResponse, profitResponse, strategyResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/reports/daily-profit?user_id=${user.id}&days=30`),
        fetch(`${API_BASE_URL}/reports/profit?user_id=${user.id}&period=${selectedPeriod}`),
        fetch(`${API_BASE_URL}/reports/strategy-performance?user_id=${user.id}&days=30`)
      ])

      const [dailyData, profitData, strategyData] = await Promise.all([
        dailyResponse.json(),
        profitResponse.json(),
        strategyResponse.json()
      ])

      setDailyData(dailyData)
      setProfitReport(profitData)
      setStrategyPerformance(strategyData)
    } catch (error) {
      console.error('Error fetching report data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit'
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
          <p className="text-gray-600">Análise detalhada do desempenho das suas apostas</p>
        </div>
        
        <div className="flex space-x-2">
          {['day', 'week', 'month'].map((period) => (
            <Button
              key={period}
              variant={selectedPeriod === period ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedPeriod(period)}
            >
              {period === 'day' ? 'Hoje' : period === 'week' ? 'Semana' : 'Mês'}
            </Button>
          ))}
        </div>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="performance">Desempenho</TabsTrigger>
          <TabsTrigger value="strategies">Estratégias</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          {profitReport && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Lucro Total</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(profitReport.total_profit)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {selectedPeriod === 'day' ? 'Hoje' : selectedPeriod === 'week' ? 'Esta semana' : 'Este mês'}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total de Apostas</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{profitReport.total_bets}</div>
                  <p className="text-xs text-muted-foreground">
                    {profitReport.winning_bets} vitórias, {profitReport.losing_bets} derrotas
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Taxa de Acerto</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{profitReport.win_rate.toFixed(1)}%</div>
                  <p className="text-xs text-muted-foreground">
                    {profitReport.winning_bets} de {profitReport.total_bets} apostas
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Lucro Médio</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(profitReport.total_bets > 0 ? profitReport.total_profit / profitReport.total_bets : 0)}
                  </div>
                  <p className="text-xs text-muted-foreground">Por aposta</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Daily Profit Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Evolução do Lucro (Últimos 30 dias)</CardTitle>
              <CardDescription>
                Acompanhe a evolução diária dos seus lucros
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                  />
                  <YAxis tickFormatter={(value) => `R$ ${value}`} />
                  <Tooltip 
                    labelFormatter={(label) => new Date(label).toLocaleDateString('pt-BR')}
                    formatter={(value, name) => [
                      formatCurrency(value), 
                      name === 'daily_profit' ? 'Lucro Diário' : 'Lucro Acumulado'
                    ]}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="daily_profit" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="daily_profit"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cumulative_profit" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="cumulative_profit"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          {/* Bet Count Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Volume de Apostas Diárias</CardTitle>
              <CardDescription>
                Quantidade de apostas realizadas por dia
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(label) => new Date(label).toLocaleDateString('pt-BR')}
                    formatter={(value) => [value, 'Apostas']}
                  />
                  <Bar dataKey="bet_count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Win Rate Distribution */}
          {profitReport && profitReport.total_bets > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Distribuição de Resultados</CardTitle>
                <CardDescription>
                  Proporção entre vitórias e derrotas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Vitórias', value: profitReport.winning_bets, color: '#00C49F' },
                        { name: 'Derrotas', value: profitReport.losing_bets, color: '#FF8042' }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {[
                        { name: 'Vitórias', value: profitReport.winning_bets, color: '#00C49F' },
                        { name: 'Derrotas', value: profitReport.losing_bets, color: '#FF8042' }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [value, 'Apostas']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="strategies" className="space-y-6">
          {/* Strategy Performance */}
          {strategyPerformance.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {strategyPerformance.map((strategy, index) => (
                <Card key={strategy.strategy_id}>
                  <CardHeader>
                    <CardTitle>Estratégia #{strategy.strategy_id}</CardTitle>
                    <CardDescription>
                      Desempenho nos últimos 30 dias
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Lucro Total</p>
                        <p className="text-lg font-semibold">
                          {formatCurrency(strategy.total_profit)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Total de Apostas</p>
                        <p className="text-lg font-semibold">{strategy.total_bets}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Taxa de Acerto</p>
                        <p className="text-lg font-semibold">{strategy.win_rate.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Lucro Médio</p>
                        <p className="text-lg font-semibold">
                          {formatCurrency(strategy.avg_profit_per_bet)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center pt-2">
                      <Badge variant={strategy.total_profit > 0 ? "default" : "destructive"}>
                        {strategy.total_profit > 0 ? "Lucrativa" : "Prejuízo"}
                      </Badge>
                      <div className="text-sm text-gray-600">
                        {strategy.winning_bets}V / {strategy.losing_bets}D
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhum dado de estratégia
                </h3>
                <p className="text-gray-600">
                  Execute algumas apostas para ver o desempenho das estratégias
                </p>
              </CardContent>
            </Card>
          )}

          {/* Strategy Comparison Chart */}
          {strategyPerformance.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Comparação de Estratégias</CardTitle>
                <CardDescription>
                  Lucro total por estratégia
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={strategyPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="strategy_id" tickFormatter={(value) => `Estratégia ${value}`} />
                    <YAxis tickFormatter={(value) => `R$ ${value}`} />
                    <Tooltip 
                      formatter={(value) => [formatCurrency(value), 'Lucro Total']}
                      labelFormatter={(label) => `Estratégia ${label}`}
                    />
                    <Bar dataKey="total_profit" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

