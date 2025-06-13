import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { ExtractedData, Invoice } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-view',
  templateUrl: './invoice-view.component.html',
  styleUrls: ['./invoice-view.component.scss']
})
export class InvoiceViewComponent implements OnInit {
  extractedData: ExtractedData | null = null;
  originalText: string = '';
  originalFile: string = '';
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  
  constructor(
    private invoiceService: InvoiceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const storedData = localStorage.getItem('extractedData');
    this.originalFile = localStorage.getItem('originalFile') || '';
    
    if (storedData) {
      this.extractedData = JSON.parse(storedData);
      this.originalText = this.extractedData?.original_text || '';
    } else {
      this.router.navigate(['/']);
    }
  }

  saveInvoice(): void {
    if (!this.extractedData) return;
    
    this.isLoading = true;
    
    const data = {
      supplier: this.extractedData.extracted_data.supplier,
      invoice: {
        invoice_number: this.extractedData.extracted_data.invoice_number,
        date: this.extractedData.extracted_data.date,
        due_date: this.extractedData.extracted_data.due_date,
        total_amount: this.extractedData.extracted_data.total_amount,
        tax_amount: this.extractedData.extracted_data.tax_amount
      },
      items: this.extractedData.extracted_data.items,
      original_extraction: this.extractedData.extracted_data,
      file_path: this.originalFile
    };
    
    this.invoiceService.saveInvoice(data).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = 'Facture enregistrée avec succès et utilisée pour l\'entraînement du modèle';
        setTimeout(() => {
          localStorage.removeItem('extractedData');
          localStorage.removeItem('originalFile');
          this.router.navigate(['/dashboard']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.error?.message || 'Une erreur est survenue lors de l\'enregistrement de la facture';
        console.error('Error saving invoice:', error);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/']);
  }
}