import sys
sys.path.append('/home/odoo/odoo_dev/odoo/')

from odoo.tools import float_round

file = open("salary2019.txt","w")

file.write("id,amount_select,condition_range_min,condition_range_max,amount_percentage,amount_fix,amount_python_compute,name,category_id,sequence,code,parent_rule_id/id,condition_select,condition_range,amount_percentage_base,register_id/id\n")

def compute_basic_bareme(value):
    if value <= 12860.0:
        basic_bareme = value * 0.2675
    elif value <= 19630.0:
        basic_bareme = 3440.05 + 0.428 * (value - 12860.00)
    elif value <= 40470.00:
        basic_bareme = 6337.61 + 0.4815 * (value - 19630.00)
    else:
        basic_bareme = 16372.07 + 0.535 * (value - 40470.0)
    return float_round(basic_bareme, precision_rounding=0.01)

def convert_to_month(value):
    return float_round(value / 12.0, precision_rounding=0.01, rounding_method='DOWN')

for bareme in [1, 2, 3]:
    if bareme == 1:
        first_amount = 555
        gross_values = [0] + list(range(first_amount, 7500 + 15, 15))
    elif bareme == 2:
        first_amount = 1065
        gross_values = [0] + list(range(first_amount, 7500 + 15, 15))
    elif bareme == 3:
        first_amount = 15
        gross_values = [0] + list(range(first_amount, 7500 + 15, 15))

    for index, gross in enumerate(gross_values):

        # PART 1: Withholding tax amount computation
        withholding_tax_amount = 0.0
        lower_bound = gross - gross % 15

        # yearly_gross_revenue = Revenu Annuel Brut
        yearly_gross_revenue = lower_bound * 12.0

        # yearly_net_taxable_amount = Revenu Annuel Net Imposable
        if yearly_gross_revenue <= 16033.33:
            yearly_net_taxable_revenue = yearly_gross_revenue * (1.0 - 0.3)
        else:
            yearly_net_taxable_revenue = yearly_gross_revenue - 4810.00

        # BAREME III: Non resident
        if bareme == 3:
            basic_bareme = compute_basic_bareme(yearly_net_taxable_revenue)
            withholding_tax_amount = convert_to_month(basic_bareme)
        else:
            # BAREME I: Isolated or spouse with income 
            if bareme == 1:
                basic_bareme = max(compute_basic_bareme(yearly_net_taxable_revenue) - 2065.10, 0.0)
                withholding_tax_amount = convert_to_month(basic_bareme)

            # BAREME II: spouse without income
            if bareme == 2:
                yearly_net_taxable_revenue_for_spouse = min(yearly_net_taxable_revenue * 0.3, 10930.0)
                basic_bareme_1 = compute_basic_bareme(yearly_net_taxable_revenue_for_spouse)
                basic_bareme_2 = compute_basic_bareme(yearly_net_taxable_revenue - yearly_net_taxable_revenue_for_spouse)
                withholding_tax_amount = convert_to_month(max(basic_bareme_1 + basic_bareme_2 - 4130.20, 0))

        if index == 0:
            lower_bound = 0
            upper_bound = first_amount
        else:
            lower_bound = gross
            upper_bound = gross + 15
        if gross == 7500:
            upper_bound = 2147483647

        if bareme == 1:
            first_id = 1
        elif bareme == 2:
            first_id = 600
        elif bareme == 3:
            first_id = 1201

        file.write("%s,fix,%s,%s,,%s,,Withholding Tax,Withholding Tax Grid 2019 (Precompte Professionnel Bareme 2019),130,P.P,hr_payroll_rules_bareme,range,GROSS,,contrib_register_pp\n" % (first_id + index, lower_bound, upper_bound, -round(withholding_tax_amount, 2)))

    file.write(",,,,,,,,,,,,,,,\n")

    for children in range(1, 21):
        if children == 1:
            withholding_tax_amount = 36.0
        if children == 2:
            withholding_tax_amount = 104.0
        if children == 3:
            withholding_tax_amount = 275.0
        if children == 4:
            withholding_tax_amount = 483.0
        if children == 5:
            withholding_tax_amount = 713.0
        if children == 6:
            withholding_tax_amount = 944.0
        if children == 7:
            withholding_tax_amount = 1174.0
        if children >= 8:
            withholding_tax_amount = 1428.0 + (children - 8) * 256.0

        result = - max(withholding_tax_amount, 0.0)

        rule_id = 1410 + children - 1
        file.write('%s,code,%s,%s,,,"result = min(%s, - (categories.PP + categories.PPRed + categories.FamRed + categories.ChA))",Child Allowance Belgium,Child Allowance Belgium,142,Ch.A,hr_payroll_rules_child,range,employee.dependent_children,,\n' % (rule_id, children, children, withholding_tax_amount))

file.close()
