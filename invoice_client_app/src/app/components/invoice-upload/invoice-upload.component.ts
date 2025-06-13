import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { ExtractedData } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-upload',
  templateUrl: './invoice-upload.component.html',
  styleUrls: ['./invoice-upload.component.scss']
})
export class InvoiceUploadComponent {
  selectedFile: File | null = null;
  isLoading = false;
  errorMessage = '';
  dragOver = false;
  
  constructor(
    private invoiceService: InvoiceService,
    private router: Router
  ) {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files ? event.target.files[0] : null;
    this.errorMessage = '';
  }

  uploadInvoice(): void {
    if (!this.selectedFile) {
      this.errorMessage = 'Veuillez sélectionner un fichier';
      return;
    }

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowedTypes.includes(this.selectedFile.type)) {
      this.errorMessage = 'Format de fichier non supporté. Veuillez télécharger un PDF ou une image (JPEG, PNG)';
      return;
    }

    this.isLoading = true;
    this.invoiceService.uploadInvoice(this.selectedFile).subscribe({
      next: (response: ExtractedData) => {
        this.isLoading = false;
        // Stocker les données extraites dans le localStorage pour les récupérer dans le composant de visualisation
        localStorage.setItem('extractedData', JSON.stringify(response));
        localStorage.setItem('originalFile', this.selectedFile?.name || '');
        this.router.navigate(['/invoice-view']);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.error?.message || 'Une erreur est survenue lors du traitement de la facture';
        console.error('Error uploading invoice:', error);
      }
    });
  }
}