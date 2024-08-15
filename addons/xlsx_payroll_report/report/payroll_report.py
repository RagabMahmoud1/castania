from odoo import models
import string


class PayrollReport(models.AbstractModel):
    _name = 'report.xlsx_payroll_report.xlsx_payroll_report' 
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        print("lines", lines)
        format1 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#d3dde3', 'color':'black', 'bottom': True, })
        format2 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True, 'bg_color':'#edf4f7', 'color':'black','num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format({'font_size':11, 'align': 'vcenter', 'bg_color':'#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size':12, 'align': 'vcenter', 'bold': False})
        # sheet = workbook.add_worksheet('Payrlip Report')

        # Fetch available salary rules:
        used_structures = []
        for sal_structure in lines.slip_ids.struct_id:
            if sal_structure.id not in used_structures:
                used_structures.append([sal_structure.id,sal_structure.name])

        # Logic for each workbook, i.e. group payslips of each salary structure into a separate sheet:
        struct_count = 1
        for used_struct in used_structures:
            # Generate Workbook
            sheet = workbook.add_worksheet(str(struct_count)+ ' - ' + str(used_struct[1]) )
            cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
            rules = []
            col_no = 7
            # Fetch available salary rules:
            for item in lines.slip_ids.struct_id.rule_ids:
                # if item.struct_id.id == used_struct[0]:
                col_title = ''
                row = [None,None,None,None,None]
                row[0] = col_no
                row[1] = item.code
                row[2] = item.name
                col_title = str(cols[col_no]) + ':' + str(cols[col_no])
                row[3] = col_title
                if len(item.name) < 8:
                    row[4] = 12
                else:
                    row[4] = len(item.name) + 2
                rules.append(row)
                col_no += 1
            # print('Salary rules to be considered for structure: ' + used_struct[1])
            # print(rules)
            #Report Details:
            # for item in lines.slip_ids:
            #     # if item.struct_id.id == used_struct[0]:
            #     batch_period = str(item.date_from.strftime('%B %d, %Y')) + '  To  ' + str(item.date_to.strftime('%B %d, %Y'))
            #     company_name = item.company_id.name
            #     break
            sheet.set_column(0, 11, 25)
            sheet.write(0,0,'Employee Name',format1)
            sheet.write(0,1,'Department',format1)
            sheet.write(0,2,'Total Salary',format1)
            sheet.write(0,3,'ID/Iqama',format1)
            sheet.write(0,4,'Bank Account No',format1)
            sheet.write(0,5,'Bank',format1)
            sheet.write(0,6,'Bank Code',format1)
            sheet.write(0,7,'Address',format1)
            sheet.write(0,8,'Basic Salary',format1)
            sheet.write(0,9,'House Rent Allowance',format1)
            sheet.write(0,10,'Other Allowances',format1)
            sheet.write(0,11,'Deductions',format1)

            x = 1
            e_name = 1
            # has_payslips = False

            for slip in lines.slip_ids:
                tot = 0.0
                basics = 0.0
                alws = 0.0
                deds = 0.0
                for line in slip.line_ids:
                    if lines.slip_ids:
                        category = line.category_id.code
                        if category == 'BASIC':
                            basic = line.total
                            basics += basic
                        if category == 'ALW':
                            alw = line.total
                            alws += alw
                        if category == 'DED':
                            ded = line.total
                            deds += -(ded)
                        if category == 'NET':
                            tot = line.total
                    has_payslips = True
                    sheet.write(e_name, 0, slip.employee_id.name, format3)
                    sheet.write(e_name, 1, slip.employee_id.department_id.name, format3)
                    sheet.write(e_name, 2, tot, format3)
                    sheet.write(e_name, 3, slip.employee_id.identification_id, format3)
                    sheet.write(e_name, 4, slip.employee_id.bank_account_id.acc_number, format3)
                    sheet.write(e_name, 5, slip.employee_id.bank_account_id.bank_id.name, format3)
                    sheet.write(e_name, 6, slip.employee_id.bank_account_id.bank_code.name, format3)
                    sheet.write(e_name, 7, slip.employee_id.address_home_id.name, format3)
                    sheet.write(e_name, 8, basics, format3)
                    sheet.write(e_name, 9, slip.employee_id.contract_id.hra, format3)
                    sheet.write(e_name, 10, alws, format3)
                    sheet.write(e_name, 11, deds, format3)

                x += 1
                e_name += 1

            # set width and height of colmns & rows:
            # sheet.set_column('A:A',35)
            # sheet.set_column('B:B',20)
            # for rule in rules:
            #     sheet.set_column(rule[3],rule[4])
            # sheet.set_column('C:C',20)
            #
            # struct_count += 1
        
