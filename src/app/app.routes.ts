import { Routes } from '@angular/router';
import { MetadataComponent } from './pages/metadata/metadata.component';
import { HomeComponent } from './pages/home/home.component';
import { CallbackComponent } from './callback/callback.component';
import { MetadataFormComponent } from './metadata-form/metadata-form.component';

export const routes: Routes = [
        { path: '', component: HomeComponent, title: 'Home' },
        { path: 'metadata-details', component: MetadataComponent, title: 'Metadata Details',
                children: [{path: 'metadata-details/form',  component:MetadataFormComponent, title: 'Metadata Form'}]},
        { path: 'oidc-callback', component: CallbackComponent }
];

export default routes;
