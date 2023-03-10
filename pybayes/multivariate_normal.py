import numpy as np
from scipy import stats

# class for multivariate normal likelihood using multivariate normal prior
# assumes known covariance
class multivariate_normal:
    def __init__(self, mu_0 = np.zeros(2), Sigma_0 = np.identity((2,2)), Sigma = np.identity((2,2))):
        self.mu_0 = mu_0
        self.Sigma_0 = Sigma_0
        self.Sigma = Sigma

    #update the parameters of the distribution
    def update_params(self, data, mu_0 = None, Sigma_0 = None, Sigma = None):
        #use default vals from initialization if none are passed
        if mu_0 == None:
            mu_0 = self.mu_0
        if Sigma_0 == None:
            Sigma_0 = self.Sigma_0
        if Sigma == None:
            Sigma = self.Sigma
    
        #make sure the data is a numpy array
        data = np.array(data)
        n = len(data)

        self.d = len(data[0])

        #assumes each observation is a row
        x_bar = np.mean(data,axis = 0)

        #Covariance matrix related calculations
        self.Sigma = Sigma
        Sigma_inv = np.linalg.inv(Sigma)
        Sigma_0_inv = np.linalg.inv(Sigma_0)

        #Sigma_n is the covariance matrix of the distribution of mean
        self.Sigma_n = np.linalg.inv(Sigma_0_inv + n * Sigma_inv)

        #mu_n is the mean
        self.mu_n = self.Sigma_n @ (n * Sigma_inv @ x_bar + Sigma_0_inv @ mu_0)

        #create var for the posterior mode of the mean vector
        self.post_mode_mu = self.mu_n

        #calculate posterior predictive parameters
        self.post_pred_mean = self.mu_n
        self.post_pred_cov = self.Sigma + self.Sigma_n
    # Posterior predictive is multivariate normal
    def sample_posterior_predictive(self,n = 1, seed = None):
        return stats.multivariate_normal(mean = self.mu_n, cov = self.post_pred_cov, size = n, random_state = seed)

class normal_inv_wishart:

    #default to two dimensional model with noninformative priors
    def __init__(self, kappa_0 = 0, nu_0 = 3, mu_0 = np.zeros(2), Sigma_0 = np.identity((2,2))):
        self.mu_0 = mu_0
        self.Sigma_0 = Sigma_0
        #kappa_0 expresses prior confidence in the mean
        self.kappa_0 = kappa_0
        #nu_0 expresses prior confidence in the covariance matrix
        self.nu_0 = nu_0

    def update_params(self, data, kappa_0 = None, nu_0 = None, mu_0 = None, Sigma_0 = None):
        #use default vals from initialization if none are passed
        if kappa_0 == None:
            kappa_0 = self.kappa_0
        if nu_0 == None:
            nu_0 = self.nu_0
        if mu_0 == None:
            mu_0 = self.mu_0
        if Sigma_0 == None:
            Sigma_0 = self.Sigma_0

        #make sure data is a numpy array
        data = data.to_numpy()

        n = len(data)
        self.d = len(data[0])

        self.kappa_n = self.kappa_0 + n
        self.nu_n = self.nu_0 + n

        S_0 = (self.nu_0 - self.d + 1)*Sigma_0
        
        x_bar = np.mean(data, axis = 0)

        self.mu_n = (1/(self.kappa_n)) * (self.kappa_0 * self.mu_0 + n * x_bar)

        #calculate sum of squares matrix
        res = data - x_bar
        if len(res) == 1:
            S = np.zeros((self.d,self.d))
        else:
            S = np.sum([np.outer(x,x) for x in res], axis = 0)

        self.S_n = S_0 + S + np.outer(x_bar - mu_0,x_bar - mu_0)*((self.kappa_0 * n)/(self.kappa_n))

        #store posterior stats as attributes
        self.post_mode_mu = self.mu_n

        self.post_mode_Sigma = self.S_n * (self.nu_n + self.d + 1)

        self.post_pred_mean = self.mu_n
        self.post_pred_cov = self.S_n * (self.kappa_n + 1)/(self.kappa_n * (self.nu_n - self.d + 1))
        self.post_pred_df = self.nu_n - self.d + 1

    def sample_posterior_predictive(self, n = 1, seed = None):
        return stats.multivariate_t(loc = self.post_pred_mean, scale = self.post_pred_cov, df = self.post_pred_df, size = n, random_state = seed)
