// app-routing.module.ts

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomeComponent } from './pages/home/home/home.component';
import { AboutComponent } from './pages/about/about/about.component';
import { ContactComponent } from './pages/contact/contact/contact.component';
import { ErrorComponent } from './pages/error/error/error.component';
import { ProductComponent } from './pages/product/product/product.component';
import { KartComponent } from './pages/kart/kart/kart.component';
import { PayComponent } from './pages/pay/pay/pay.component';
import { ProfileComponent } from './pages/profile/profile/profile.component';
import { UserManagementComponent } from './pages/user_management/user-management/user-management.component'

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'error', component: ErrorComponent },
  { path: 'product', component: ProductComponent },
  { path: 'kart', component: KartComponent },
  { path: 'pay', component: PayComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'user_management', component: UserManagementComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
