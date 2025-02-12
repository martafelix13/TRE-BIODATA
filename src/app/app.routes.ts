import { Routes } from '@angular/router';
import { MetadataComponent } from './pages/metadata/metadata.component';
import { HomeComponent } from './pages/home/home.component';

export const routes: Routes = [
        { path: '', component: HomeComponent, title: 'Home' },
        { path: 'metadata-details', component: MetadataComponent, title: 'Metadata Details' },
];

export default routes;
