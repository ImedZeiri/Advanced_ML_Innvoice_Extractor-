import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { InvoiceUploadComponent } from './components/invoice-upload/invoice-upload.component';
import { InvoiceViewComponent } from './components/invoice-view/invoice-view.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';

const routes: Routes = [
  { path: '', component: InvoiceUploadComponent },
  { path: 'invoice-view', component: InvoiceViewComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
