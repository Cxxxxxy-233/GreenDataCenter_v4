// 模拟数据文件
const mockInvestmentBreakdown = {
  powerSupplyCapexLakh: 4200,
  greenPowerCapexLakh: 8600,
  coolingCapexLakh: 2200
}

const totalCapexLakh =
  mockInvestmentBreakdown.powerSupplyCapexLakh +
  mockInvestmentBreakdown.greenPowerCapexLakh +
  mockInvestmentBreakdown.coolingCapexLakh

const budgetConstraintLakh = 15000
const budgetDeltaLakh = budgetConstraintLakh - totalCapexLakh
const rackCount = 1024
const costPerRack = Number((totalCapexLakh / rackCount).toFixed(2))
const roi = 0.102
const paybackPeriod = 9.8

export const mockSolutionData = {
  id: 'mock-solution-001',
  created_at: new Date().toISOString(),
  name: '乌兰察布数据中心绿电消纳方案',
  confidence: 0.92,
  overall_scores: {
    overall: 0.85,
    economic: 0.82,
    reliability: 0.88,
    environmental: 0.89
  },
  key_metrics: {
    total_cost: totalCapexLakh,
    pue: 1.23,
    green_power_ratio: 0.72,
    tier_level: 3,
    expected_availability: 0.9998,
    annual_carbon_emission: 28600,
    cost_per_rack: costPerRack,
    roi,
    payback_period: paybackPeriod
  },
  final_report: `# 乌兰察布数据中心绿电消纳方案报告

## 执行摘要

本方案针对位于乌兰察布的新建数据中心项目，提出了一套完整的绿电消纳解决方案，旨在实现72%的绿电消纳率目标，同时确保系统可靠性符合Tier 3标准。

### 关键指标
- **推荐制冷技术**: 传统房间级CRAC(上送风)+热通道封闭
- **预测PUE**: 1.23
- **绿电消纳率**: 72%
- **总投资**: ${totalCapexLakh}万元

## 综合评分
- **经济性**: 82%
- **可靠性**: 88%
- **环保性**: 89%
- **总体**: 85%

## 关键指标

| 指标 | 数值 |
|------|------|
| 总成本(万元) | ${totalCapexLakh.toFixed(2)} |
| PUE | 1.230 |
| 绿电比例 | 72.0% |
| Tier 等级 | 3 |
| 预期可用性 | 0.9998 |
| 年碳排放(吨) | 28600 |

## 经济性方案

### 投资结构分析
本项目总投资为${totalCapexLakh}万元，其中供电系统投资约${mockInvestmentBreakdown.powerSupplyCapexLakh}万元，绿电系统投资约${mockInvestmentBreakdown.greenPowerCapexLakh}万元，制冷系统投资约${mockInvestmentBreakdown.coolingCapexLakh}万元。

### 经济指标
- **总投资**: ${totalCapexLakh}万元
- **单机柜成本**: ${costPerRack}万元
- **投资回报率(ROI)**: ${(roi * 100).toFixed(1)}%
- **投资回收期**: ${paybackPeriod}年

### 建议
1. 考虑分阶段建设，先完成第一期20MW，验证效果后再扩大规模
2. 建议与当地电网公司签订长期购电协议，锁定电价
3. 积极申请绿色电力证书和碳排放交易收益

## 供电可靠性方案

### 系统架构
- **外部电压**: 35kV
- **冗余配置**: 主变N+1，配变2N（互为备用）
- **母线类型**: 380/220V 单母线分段接线
- **UPS配置**: 2N UPS系统，电池后备时间30分钟

### 可靠性指标
- **系统可用性**: 99.98%
- **年停机时间**: 1.75小时
- **Tier等级**: 3

### 建议
1. 建议配置两套独立的外部电源进线
2. 定期进行UPS电池测试和维护
3. 建立完善的电力监控系统

## 环保方案

### 绿电配置
- **光伏装机容量**: 15MW
- **风电装机容量**: 10MW
- **储能容量**: 45MWh

### 环保指标
- **绿电消纳率**: 72%
- **年碳减排量**: 约58000吨CO₂
- **PUE目标**: 1.23

### 建议
1. 建议参与绿色电力交易市场，扩大绿电来源
2. 考虑余热回收利用，提高能源效率
3. 建立碳足迹监测系统

## 关键权衡

1. **绿电比例 vs 投资成本**: 通过优化风光储配置比例，在72%绿电目标下实现最优投资
2. **PUE优化 vs 制冷投资**: 采用传统CRAC+热通道封闭方案，在PUE和投资间取得平衡
3. **储能容量 vs 供电可靠性**: 配置45MWh储能，既保证绿电消纳又提高供电可靠性

## 风险清单

1. **[技术风险]** 风光资源不确定性：可能导致实际绿电消纳率低于预期
2. **[市场风险]** 电价波动：可能影响投资回报
3. **[政策风险]** 补贴政策变化：可能影响项目收益

## 最终建议

1. 建议采用本方案，可实现72%绿电消纳率目标
2. 建议与当地政府和电网公司深入沟通，争取政策支持
3. 建议在项目实施过程中进行详细的勘测和设计
4. 建议建立完善的运营监控和维护体系
`,
  intermediate_results: {
    requirement_parser: {
      requirement: {
        location: '乌兰察布',
        planned_load_kw: 50000,
        green_power_ratio: 0.7,
        planned_area: 20000,
        budget_constraint: 15000,
        cooling_technology: '传统房间级CRAC(上送风)+热通道封闭',
        machine_room_grade: '3',
        pue_target: 1.25,
        sim_hours: 168,
        year: 2025
      }
    },
    draft_plan_agent: {
      full_output: {
        green_power_result: {
          inputs: {
            location: '乌兰察布',
            green_power_ratio: 0.7,
            load_mw: 50,
            sim_hours: 168,
            year: 2025,
            date: null,
            bounds: {
              wind_capacity_bounds: [1, 500],
              pv_capacity_bounds: [1, 500],
              storage_capacity_bounds: [20, 500]
            },
            week_start_hour: 0,
            maxiter: 60,
            popsize: 10,
            seed: 42
          },
          generated_files: {
            pv_csv: 'outputs/PV.csv',
            wind_csv: 'outputs/Wind.csv',
            load_csv: 'outputs/Load.csv',
            balance_plot: 'outputs/green_power_balance_wulanchabu_168h.png'
          },
          pv_profile: {
            mode: '8760h',
            time_range: '2025-01-01 00:00 ~ 2025-12-31 23:00',
            summary: '根据乌兰察布气象条件生成全年光伏单位出力曲线，正南朝向，倾角采用当地推荐值。'
          },
          wind_profile: {
            mode: '8760h',
            time_range: '2025-01-01 00:00 ~ 2025-12-31 23:00',
            summary: '依据当地风速特征和风机切入/额定/切出风速生成全年风电单位出力曲线。'
          },
          optimization: {
            wind_capacity_mw: 10,
            pv_capacity_mw: 15,
            storage_capacity_mwh: 45,
            achieved_green_ratio: 0.72,
            total_cost: 8600,
            details: {
              wind_capex_lakh: 3500,
              pv_capex_lakh: 3150,
              storage_capex_lakh: 1950
            }
          }
        },
        cooling_result: {
          cooling_technology: '传统房间级CRAC(上送风)+热通道封闭',
          estimated_pue: 1.23,
          predicted_wue: 1.65,
          cooling_power_consumption: 7960,
          waste_heat_recovery_kw: 3200,
          cooling_kpis: {
            cooling_load_kw: 50000,
            cooling_power_kw: 7960,
            corrected_cop: 6.28,
            waste_heat_recovery_kw: 3200
          },
          economic_indicators: {
            initial_investment: 2200,
            annual_op_cost: 380,
            annual_electricity_cost: 320,
            lcoe: 0.28
          },
          strategy_optimization_trace: [
            { score: 1.35, iteration: 1 },
            { score: 1.31, iteration: 2 },
            { score: 1.28, iteration: 3 },
            { score: 1.26, iteration: 4 },
            { score: 1.25, iteration: 5 },
            { score: 1.24, iteration: 6 },
            { score: 1.23, iteration: 7 },
            { score: 1.23, iteration: 8 }
          ],
          optimization_summary: {
            optimization_mode: 'weighted_multi_objective',
            priority_mode: 'economic',
            feasible_strategy_count: 4,
            selected_strategy: '传统房间级CRAC(上送风)+热通道封闭',
            objective_weights: {
              PUE: 0.32,
              WUE: 0.18,
              TCO: 0.28,
              CUE: 0.12,
              WHR: 0.10
            }
          },
          all_strategy_scores: [
            {
              strategy: '传统房间级CRAC(上送风)+热通道封闭',
              total_score: 1.23,
              ranking: 1,
              pue: 1.23,
              wue: 1.65,
              tco: 0.84,
              cue: 0.78,
              whr: 0.66
            },
            {
              strategy: '冷冻水型水冷冷水机组+行级空调',
              total_score: 1.31,
              ranking: 2,
              pue: 1.20,
              wue: 1.92,
              tco: 0.93,
              cue: 0.74,
              whr: 0.58
            },
            {
              strategy: '蒸发冷却+冷冻水末端',
              total_score: 1.37,
              ranking: 3,
              pue: 1.18,
              wue: 2.36,
              tco: 0.91,
              cue: 0.76,
              whr: 0.52
            },
            {
              strategy: '浸没式液冷+余热回收',
              total_score: 1.42,
              ranking: 4,
              pue: 1.15,
              wue: 1.02,
              tco: 1.08,
              cue: 0.71,
              whr: 0.88
            }
          ]
        },
        power_supply_plan: {
          scheme_name: 'A级-35kV供电一体化方案',
          external_voltage: '35kV',
          secondary_voltage: '380V/220V',
          external_source_type: '双路35kV独立进线',
          redundancy_logic: '主变N+1，配变2N（互为备用）',
          bus_type: '380/220V 单母线分段接线',
          diesel_status: '配置N+1备用柴油发电机组',
          reasons: '【配置等级】: 选定 A 级供电架构，符合A级容错标准，确保单一组件故障时不影响业务。\n【外部供电】: 采用 35kV 接入，理由：适用于30~60MVA中小型数据中心。\n【次级配电】: 选定 10kV 方案，原因：10kV在设备费与占地上均为最优，配变单台推荐2.5MVA以适配0.4kV断路器能力。\n【电气接线】: 主机房采用 380/220V 单母线分段接线，确保电力分配的可靠性。',
          raw_json: {
            machine_room_grade: 'A',
            total_load_mw: 50,
            total_load_mva: 55.56,
            pue_target: 1.25,
            power_factor: 0.9,
            main_transformers: '主变N+1',
            distribution_transformers: '2.5 MVA / 2N',
            cost_per_mw: 84
          }
        }
      }
    },
    cost_calculation: {
      full_output: {
        economic_analysis_result: {
          total_capex_lakh: totalCapexLakh,
          is_over_budget: false,
          budget_constraint_lakh: budgetConstraintLakh,
          budget_delta_lakh: budgetDeltaLakh,
          capex_breakdown: {
            power_supply_system_lakh: mockInvestmentBreakdown.powerSupplyCapexLakh,
            green_power_system_lakh: mockInvestmentBreakdown.greenPowerCapexLakh,
            details: {
              wind_capex_lakh: 3500,
              pv_capex_lakh: 3150,
              storage_capex_lakh: 1950
            }
          }
        }
      }
    },
    economic_analysis: {
      full_output: {
        expert_type: 'economic',
        expert_name: 'Economic Analysis Expert-Zhang',
        summary: `方案经济性整体可接受，总投资${totalCapexLakh}万元，已与预算上限持平。投资回报率约${(roi * 100).toFixed(1)}%，投资回收期约${paybackPeriod}年，需在建设节奏与运维优化上继续控制成本。`,
        scores: { cost_efficiency: 0.85, roi: 0.78 },
        metrics: {
          total_cost: totalCapexLakh,
          cost_per_rack: costPerRack,
          roi,
          payback_period: paybackPeriod
        },
        recommendations: [
          '建议分阶段建设，降低初期投资压力',
          '建议签订长期购电协议，锁定电价风险',
          '建议积极申请绿色电价和补贴政策'
        ],
        concerns: [
          '电价波动可能影响投资回报',
          '运维成本需要严格控制'
        ],
        confidence: 0.88
      }
    },
    power_reliability_analysis: {
      full_output: {
        expert_type: 'power_reliability',
        expert_name: 'Power Reliability Expert-Li',
        summary: '供电系统设计符合Tier 3标准，采用2N冗余配置，系统可用性达到99.98%，可靠性表现优秀。',
        scores: { reliability: 0.92, availability: 0.94 },
        metrics: {
          tier_level: 3,
          expected_availability: 0.9998,
          annual_downtime: 1.75,
          ups_configuration: '2N UPS',
          ups_capacity: 60,
          distribution_reliability: 0.995
        },
        recommendations: [
          '建议配置两套独立的外部电源进线',
          '建议定期进行UPS电池测试和维护',
          '建议建立完善的电力监控系统'
        ],
        concerns: [
          '外部电网稳定性需要持续关注',
          '备用发电机需定期演练'
        ],
        confidence: 0.90
      }
    },
    environmental_analysis: {
      full_output: {
        expert_type: 'environmental',
        expert_name: 'Environmental Analysis Expert-Wang',
        summary: '绿电方案设计合理，绿电消纳率达72%，PUE达1.23，环保表现优秀，年碳减排约5.8万吨。',
        scores: {
          environmental_score: 0.90,
          pue_score: 0.88,
          green_power_score: 0.92,
          carbon_efficiency: 0.85
        },
        metrics: {
          pue_target: 1.23,
          green_power_ratio: 0.72,
          annual_carbon_emission: 28600,
          carbon_per_rack: 28
        },
        recommendations: [
          '建议参与绿色电力交易市场',
          '建议考虑余热回收利用',
          '建议建立碳足迹监测系统'
        ],
        concerns: [
          '风光资源存在年度波动',
          '储能电池回收需提前规划'
        ],
        confidence: 0.87
      }
    },
    debate_round: [
      {
        round: 1,
        speaker: 'Economic Analysis Expert-Zhang',
        content: '建议适当降低储能配置，虽然会略微减少绿电消纳率，但可以显著降低投资成本，提高投资回报率。'
      },
      {
        round: 1,
        speaker: 'Environmental Analysis Expert-Wang',
        content: '我不同意，降低储能会影响绿电消纳的稳定性，我们需要保证在风光资源不足时仍能维持较高的绿电比例。'
      },
      {
        round: 1,
        speaker: 'Power Reliability Expert-Li',
        content: '我认为可以在两者间取得平衡，储能配置可以适当调整，但需要保证供电可靠性不受影响。'
      },
      {
        round: 2,
        speaker: 'Economic Analysis Expert-Zhang',
        content: '经过重新评估，我同意维持当前的储能配置，这样可以更好地应对风光资源波动。'
      },
      {
        round: 2,
        speaker: 'Environmental Analysis Expert-Wang',
        content: '很好，我相信当前的配置能够在经济性和环保性之间取得良好平衡。'
      }
    ],
    arbitrator: {
      full_output: {
        summary: `综合三位专家的意见，当前方案在经济性、可靠性和环保性方面保持均衡，绿电消纳率72%，PUE1.23，总投资${totalCapexLakh}万元，当前已与预算上限持平，建议在控制实施节奏的前提下采用此方案。`,
        consensus_score: 0.85,
        scores: {
          overall: 0.85,
          economic: 0.82,
          reliability: 0.88,
          environmental: 0.89
        },
        trade_offs: [
          { conflict: '绿电比例 vs 投资成本', resolution: '通过优化风光储配置比例，在72%绿电目标下实现最优投资' },
          { conflict: 'PUE优化 vs 制冷投资', resolution: '采用传统CRAC+热通道封闭方案，在PUE和投资间取得平衡' },
          { conflict: '储能容量 vs 供电可靠性', resolution: '配置45MWh储能，既保证绿电消纳又提高供电可靠性' }
        ],
        recommendations: [
          '建议采用本方案，可实现72%绿电消纳率目标',
          '建议与当地政府和电网公司深入沟通，争取政策支持',
          '建议在项目实施过程中进行详细的勘测和设计',
          '建议建立完善的运营监控和维护体系'
        ],
        risks: [
          { type: '技术风险', description: '风光资源不确定性：可能导致实际绿电消纳率低于预期' },
          { type: '市场风险', description: '电价波动：可能影响投资回报' },
          { type: '政策风险', description: '补贴政策变化：可能影响项目收益' }
        ]
      }
    },
    final_report: {
      full_output: {
        path: '/data/reports/mock-solution-001.md',
        word_count: 3520
      }
    }
  },
  debate_history: [
    {
      round: 1,
      speaker: 'Economic Analysis Expert-Zhang',
      content: '建议适当降低储能配置，虽然会略微减少绿电消纳率，但可以显著降低投资成本，提高投资回报率。'
    },
    {
      round: 1,
      speaker: 'Environmental Analysis Expert-Wang',
      content: '我不同意，降低储能会影响绿电消纳的稳定性，我们需要保证在风光资源不足时仍能维持较高的绿电比例。'
    },
    {
      round: 1,
      speaker: 'Power Reliability Expert-Li',
      content: '我认为可以在两者间取得平衡，储能配置可以适当调整，但需要保证供电可靠性不受影响。'
    },
    {
      round: 2,
      speaker: 'Economic Analysis Expert-Zhang',
      content: '经过重新评估，我同意维持当前的储能配置，这样可以更好地应对风光资源波动。'
    },
    {
      round: 2,
      speaker: 'Environmental Analysis Expert-Wang',
      content: '很好，我相信当前的配置能够在经济性和环保性之间取得良好平衡。'
    }
  ],
  economic_section: {
    description: `方案经济性整体可接受，总投资${totalCapexLakh}万元，已与预算上限持平。投资回报率约${(roi * 100).toFixed(1)}%，投资回收期约${paybackPeriod}年，需要通过分阶段建设和运维优化进一步提升收益表现。`,
    content: {
      total_cost: totalCapexLakh,
      cost_per_rack: costPerRack,
      roi,
      payback_period: paybackPeriod
    },
    recommendations: [
      '建议分阶段建设，降低初期投资压力',
      '建议签订长期购电协议，锁定电价风险',
      '建议积极申请绿色电价和补贴政策'
    ]
  },
  power_reliability_section: {
    description: '供电系统设计符合Tier 3标准，采用2N冗余配置，系统可用性达到99.98%，可靠性表现优秀。',
    content: {
      tier_level: 3,
      expected_availability: 0.9998,
      ups_configuration: '2N UPS',
      ups_capacity: 60
    },
    recommendations: [
      '建议配置两套独立的外部电源进线',
      '建议定期进行UPS电池测试和维护',
      '建议建立完善的电力监控系统'
    ]
  },
  environmental_section: {
    description: '绿电方案设计合理，绿电消纳率达72%，PUE达1.23，环保表现优秀，年碳减排约5.8万吨。',
    content: {
      pue: 1.23,
      green_power_ratio: 0.72,
      annual_carbon_emission: 28600
    },
    recommendations: [
      '建议参与绿色电力交易市场',
      '建议考虑余热回收利用',
      '建议建立碳足迹监测系统'
    ]
  }
}

// 模拟配置表单数据
export const mockConfigData = {
  location: '乌兰察布',
  planned_load_kw: 50000,
  green_power_ratio: 0.7,
  planned_area: 20000,
  budget_constraint: 15000,
  cooling_technology: '传统房间级CRAC(上送风)+热通道封闭',
  machine_room_grade: '3',
  pue_target: 1.25,
  sim_hours: 168,
  year: 2025
}

// 模拟历史方案列表
export const mockSolutionsList = [
  {
    id: 'mock-solution-001',
    name: '乌兰察布数据中心绿电消纳方案',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    location: '乌兰察布',
    green_ratio: 0.72,
    total_cost: totalCapexLakh,
    pue: 1.23
  },
  {
    id: 'mock-solution-002',
    name: '张家口数据中心绿电消纳方案',
    created_at: new Date(Date.now() - 172800000).toISOString(),
    location: '张家口',
    green_ratio: 0.65,
    total_cost: 9800,
    pue: 1.28
  },
  {
    id: 'mock-solution-003',
    name: '大同数据中心绿电消纳方案',
    created_at: new Date(Date.now() - 259200000).toISOString(),
    location: '大同',
    green_ratio: 0.7,
    total_cost: 11200,
    pue: 1.25
  }
]
