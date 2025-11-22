from io import StringIO
import pandas as pd

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import EquipmentDataset
from .serializers import EquipmentDatasetSerializer
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

#View 1: CSV Upload
class UploadCSVView(APIView):
    parser_classes = [MultiPartParser]  # Handle file uploads
    permission_classes = [IsAuthenticated]  # Require login
    
    def post(self, request):
        try:
            # Step 1: Get the uploaded file from request
            file_obj = request.FILES['file']
            
            # Step 2: Read CSV into pandas DataFrame
            df = pd.read_csv(file_obj)
            
            # Step 3: Calculate statistics
            total_count = len(df)  # Number of rows
            avg_flowrate = df['Flowrate'].mean()  # Average of Flowrate column
            avg_pressure = df['Pressure'].mean()
            avg_temperature = df['Temperature'].mean()
            
            # Step 4: Count equipment by type
            # Example: {'Pump': 4, 'Valve': 3, ...}
            type_distribution = df['Type'].value_counts().to_dict()
            
            # Step 5: Save to database WITH USER
            dataset = EquipmentDataset.objects.create(
                user=request.user,  # ADD THIS LINE - IMPORTANT!
                filename=file_obj.name,
                total_count=total_count,
                avg_flowrate=avg_flowrate,
                avg_pressure=avg_pressure,
                avg_temperature=avg_temperature,
                csv_data=df.to_csv(index=False)  # Convert back to CSV string
            )
            
            # Step 6: Keep only last 5 datasets per user
            old_datasets = EquipmentDataset.objects.filter(user=request.user).order_by('-upload_date')[5:]
            for old in old_datasets:
                old.delete()
            
            # Step 7: Return response to frontend
            return Response({
                'id': dataset.id,
                'total_count': total_count,
                'averages': {
                    'flowrate': round(avg_flowrate, 2),
                    'pressure': round(avg_pressure, 2),
                    'temperature': round(avg_temperature, 2)
                },
                'type_distribution': type_distribution,
                'data': df.to_dict('records')  # Convert DataFrame to list of dicts
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If anything goes wrong, return error
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#View 2: History
class HistoryView(APIView):
    """
    History View - Returns last 5 uploaded datasets WITH full summaries
    Including total count, averages, AND equipment type distribution
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get last 5 datasets for the authenticated user
            datasets = EquipmentDataset.objects.filter(user=request.user).order_by('-upload_date')[:5]
            
            # Serialize with complete summary information
            history_data = []
            for dataset in datasets:
                # Parse CSV data to get type distribution
                df = pd.read_csv(StringIO(dataset.csv_data))
                type_distribution = df['Type'].value_counts().to_dict()
                
                history_data.append({
                    'id': dataset.id,
                    'filename': dataset.filename,
                    'upload_date': dataset.upload_date.isoformat(),
                    'summary': {
                        'total_count': dataset.total_count,
                        'avg_flowrate': round(dataset.avg_flowrate, 2),
                        'avg_pressure': round(dataset.avg_pressure, 2),
                        'avg_temperature': round(dataset.avg_temperature, 2),
                        'type_distribution': type_distribution  # ADD THIS
                    }
                })
            
            return Response(history_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import EquipmentDataset
import pandas as pd
from io import StringIO

#View 3: PDF Generation - ENHANCED
class GeneratePDFView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, dataset_id):
        try:
            # Get specific dataset from database
            dataset = EquipmentDataset.objects.get(id=dataset_id)
            
            # Create BytesIO buffer
            buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#007bff'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#007bff'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            story.append(Paragraph("Equipment Analysis Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Report Info
            report_info = f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            report_info += f"<b>File:</b> {dataset.filename}<br/>"
            report_info += f"<b>Upload Date:</b> {dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(report_info, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Summary Statistics Section
            story.append(Paragraph("Summary Statistics", heading_style))
            summary_data = [
                ['Metric', 'Value'],
                ['Total Equipment Count', str(dataset.total_count)],
                ['Average Flowrate', f"{dataset.avg_flowrate:.2f}"],
                ['Average Pressure', f"{dataset.avg_pressure:.2f}"],
                ['Average Temperature', f"{dataset.avg_temperature:.2f}"]
            ]
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Equipment Type Distribution
            story.append(Paragraph("Equipment Type Distribution", heading_style))
            df = pd.read_csv(StringIO(dataset.csv_data))
            type_dist = df['Type'].value_counts().to_dict()
            
            type_data = [['Equipment Type', 'Count']]
            for equip_type, count in type_dist.items():
                type_data.append([equip_type, str(count)])
            
            type_table = Table(type_data, colWidths=[3*inch, 2*inch])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(type_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Equipment Data Table
            story.append(PageBreak())
            story.append(Paragraph("Equipment Details", heading_style))
            
            # Prepare table data
            equipment_data = df.to_dict('records')
            table_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
            
            for item in equipment_data:
                table_data.append([
                    str(item.get('Equipment Name', '')),
                    str(item.get('Type', '')),
                    str(item.get('Flowrate', '')),
                    str(item.get('Pressure', '')),
                    str(item.get('Temperature', ''))
                ])
            
            data_table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            story.append(data_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            story.append(Spacer(1, 0.2*inch))
            footer_text = "<i>This report was automatically generated by the Chemical Equipment Parameter Visualizer system.</i>"
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Return PDF
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{dataset.filename}_report.pdf"'
            
            return response
            
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#View 4: Authentication
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Validate username and password
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Get or create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return token to frontend
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })


