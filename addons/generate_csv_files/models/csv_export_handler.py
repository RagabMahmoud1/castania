from odoo import models, fields
import io
import base64
import csv
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    def generate_csv(self, data, filename, recid, modelname, delimiter='\t'):
        # Ensure the filename has a .csv extension
        #if not filename.lower().endswith('.csv'):
        #    filename += '.csv'

        # Create a CSV file in memory
        output = io.StringIO()
        #writer = csv.writer(output)
        writer = csv.writer(output, delimiter=delimiter)
        try:
            # Write the header row
            if data:
                writer.writerow(data[0].keys())  # Header
                
                # Write data rows
                for row in data:
                    writer.writerow(row.values())

            # Convert the data to a base64 string
            csv_data = base64.b64encode(output.getvalue().encode('utf-8')).decode('utf-8')

            # Create or update the attachment
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': csv_data,
                'res_model': modelname,
                'res_id': recid,
                'type': 'binary',
            })

            # Link the attachment to the mail.message record
            self.attachment_ids = [(4, attachment.id)]

        except Exception as e:
            _logger.error(f"Error generating the file: {str(e)}")
            raise

        finally:
            # Reset output
            output.close()
