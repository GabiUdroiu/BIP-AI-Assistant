import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { DashboardComponent } from './dashboard/dashboard.component';

export const routes: Routes = [
  { path: '', component: ChatComponent },
  { path: 'dashboard', component: DashboardComponent }
];
