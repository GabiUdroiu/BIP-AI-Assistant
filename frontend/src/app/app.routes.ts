import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { CameraComponent } from './camera/camera.component';

export const routes: Routes = [
  { path: '', component: ChatComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'camera', component: CameraComponent }
];
