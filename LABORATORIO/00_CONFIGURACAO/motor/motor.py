"""Motor financeiro do Laboratório. Valores em R$ mil nominais por ano (anos 1..10, idade 19->29).
Premissas globais explícitas abaixo. Não é previsão: é modelo de cenários."""
INFL = 0.045          # inflação média a.a.
RET = 0.10            # retorno líquido nominal da carteira pessoal
DEBT_RATE = 0.14      # custo da dívida empresarial
LIAB_RATE = 0.12      # custo da dívida pessoal (financiamento)
STAKE_HAIRCUT = 0.30  # desconto de iliquidez sobre participação (valuation != caixa)
BOLSA = [7.2]*4 + [0]*6   # bolsa/permanência R$600/mês nos 4 anos de graduação (PENDENTE confirmar)
L = [24, 28, 32, 36, 48, 60, 72, 84, 96, 108]  # custo de vida base (SP, nominal)
DEFLATOR10 = (1+INFL)**10
Z = lambda: [0.0]*10
DEFAULTS = dict(SAL=Z(), OTH=Z(), OUT=Z(), REV=Z(), GM=Z(), OM=Z(), TAX=Z(), PL=Z(), DIV=Z(), WC=Z(),
    CAPEX=Z(), EQ=Z(), INJ=Z(), DEBT_IN=Z(), DEBT_PAY=Z(), OWN=[1.0]*10, VM=Z(), REC=Z(),
    assets_inv=Z(), assets_g=0.08, assets_y=0.0, liab_in=Z(), liab_pay=Z(), shutdown=None,
    living_mult=1.0, creep=0.40, div_share=False)  # div_share=True: dividendo pessoal = dividendo * participação

SCEN = {"pessimista": dict(rev_m=0.6, om_d=-0.05, sal_m=0.88, val_m=0.6),
        "base":       dict(rev_m=1.0, om_d=0.0,   sal_m=1.0,  val_m=1.0),
        "otimista":   dict(rev_m=1.5, om_d=0.04,  sal_m=1.15, val_m=1.4)}

def run(p, rev_m=1.0, om_d=0.0, sal_m=1.0, val_m=1.0):
    p = {**DEFAULTS, **p}
    cash = debt = wc_prev = cumcapex = 0.0
    wealth, assets, liab = 1.0, 0.0, 0.0     # capital inicial R$1.000
    dead = False; rows = []; acc = dict(fat=0, lop=0, net=0, div=0, inc=0, pl=0)
    for y in range(10):
        rev = 0.0 if dead else p['REV'][y]*rev_m
        gp = rev*p['GM'][y]
        om = p['OM'][y] + (om_d if rev > 0 else 0)
        pre = rev*om
        pl = 0.0 if dead else p['PL'][y]
        lop = pre - pl
        interest = debt*DEBT_RATE
        imp = rev*p['TAX'][y]
        net = lop - imp - interest
        wc = rev*p['WC'][y]; dwc = wc - wc_prev; wc_prev = wc
        capex = 0.0 if dead else p['CAPEX'][y]; cumcapex += capex
        eq, inj, din = p['EQ'][y], p['INJ'][y], p['DEBT_IN'][y]
        dpay = min(p['DEBT_PAY'][y], debt+din)
        fcf = net - dwc - capex
        cash_pre = cash + fcf + eq + inj + din - dpay
        debt = debt + din - dpay
        if cash_pre < 0: debt += -cash_pre; cash_pre = 0.0     # déficit financiado por dívida
        avail = max(0.0, cash_pre - 0.08*rev)                   # caixa mínimo = 8% da receita
        sweep = min(debt, avail); debt -= sweep; avail -= sweep  # caixa excedente quita dívida primeiro
        div = min(p['DIV'][y]*max(0, net), avail)
        cash = cash_pre - sweep - div
        baixa = (p['shutdown'] == y)
        val = 0.0 if (dead or baixa) else rev*p['VM'][y]*val_m
        stake = p['OWN'][y]*val
        book = cash + wc + cumcapex - debt
        if baixa:
            cash = debt = wc_prev = cumcapex = 0.0; book = 0.0; dead = True
        pl_net = pl*0.85
        div_p = div*(p['OWN'][y] if p['div_share'] else 1.0)
        div_net = div_p - 0.10*max(0, div_p-600)
        ay = assets*p['assets_y']
        inc = p['SAL'][y]*sal_m + p['OTH'][y] + BOLSA[y] + pl_net + div_net + ay
        living = max(L[y]*p['living_mult'], p['creep']*inc)
        lint = liab*LIAB_RATE
        ainv, lin = p['assets_inv'][y], p['liab_in'][y]
        lpay = min(p['liab_pay'][y], liab+lin)
        sav = inc - living - inj - (ainv-lin) - lpay - lint - p['OUT'][y]
        wealth = wealth*(1+RET if wealth >= 0 else 1.20) + sav
        assets = assets*(1+p['assets_g']) + ainv
        liab = liab + lin - lpay
        pers = wealth + assets - liab
        for k, v in dict(fat=rev, lop=lop, net=net, div=div, inc=inc, pl=pl_net).items(): acc[k] += v
        rows.append(dict(ano=y+1, idade=20+y, fat=rev, rec=rev*p['REC'][y], gp=gp, gm=(gp/rev if rev else 0),
            lop=lop, imp=imp, juros=interest, net=net, fcf=fcf, wc=wc, cash=cash if not baixa else 0.0,
            pl=pl_net, div=div, inc=inc, living=living, sav=sav, wealth=wealth, assets=assets,
            pers=pers, debt_emp=debt if not baixa else 0.0, debt_pess=liab+max(0, -wealth),
            own=p['OWN'][y], val=val, stake=stake, book=book, baixa=baixa,
            fat_ac=acc['fat'], lop_ac=acc['lop'], net_ac=acc['net'], div_ac=acc['div'], inc_ac=acc['inc'], pl_ac=acc['pl']))
    f = rows[-1]
    out = dict(rows=rows, pers=f['pers'], stake=f['stake'], adj=f['pers']+(1-STAKE_HAIRCUT)*f['stake'],
               inc_m=f['inc']/12, inc_ac=f['inc_ac'], cash=f['cash'], fat=f['fat'], val=f['val'])
    out['adj_real'] = out['adj']/DEFLATOR10
    return out

def scenarios(p, override=None):
    r = {}
    for k, kw in SCEN.items():
        kw = dict(kw); kw.update((override or {}).get(k, {}))
        r[k] = run(p, **kw)
    return r
