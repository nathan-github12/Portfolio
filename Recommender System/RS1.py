import sys
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial
from sklearn.model_selection import train_test_split
import statistics
import warnings
warnings.filterwarnings("ignore")


class RS:
    def __init__(self, userId, epochs = 20, lmb = 0.02, latentDims = 3, trainingRate = 0.005):
        #Initialises and assigns variables to be used throughout the class.   
        self.database = pd.read_csv("./userItem.csv", low_memory=False)
        self.movies = pd.read_csv("./ml-latest-small/movies.csv", low_memory=False)
        self.UID = userId
        self.epochs = epochs
        self.lmb = lmb
        self.latentDims = latentDims
        self.trainingRate = trainingRate

    def newUser(self) -> None:
        #Handles new users by assigning them a new user id and prompting them
        #to rate 5 movies they have previously seen.
        self.UID = int(self.database.index.max()) + 1
        print("Your New User ID = :", self.UID)
        newMoviesDict = {}
        for i in range(5):
            searchCriteria  = input("Please search for a movie you have seen and give it a rating.")
            results = (self.movies[self.movies['title'].str.contains(searchCriteria) == True])
            print("Movies matching your criteria: \n", results['title'])
            selectedID = int(input("Please select the movie ID you wish to rate: \n"))
            givenRating = float(input("Please give a rating of the selected movie (0.0 - 5.0) \n"))
            newMoviesDict[selectedID] = givenRating
        
        self.database = self.database.append(newMoviesDict, ignore_index=True)
    
        return self.UID

    def currentUser(self):

        #Handles current users by giving a selection of current user id's to get recommendations for.
        print("[0]  10")
        print("[1]  34")
        print("[2]  67")
        selectedUser = int(input("Select a current user to get recommendations for!"))

        if selectedUser == 0:
            self.UID = 10
        elif selectedUser == 1:
            self.UID = 34
        elif selectedUser == 2:
            self.UID == 67
        else:
            print('Please select from the list of available users.')

        return self.UID

    def preprocessing(self):
        #Replaces any NaN values in the dataset with 0.
        ratingsMatrix = self.database.fillna(0).values

        return ratingsMatrix

    def trainTestSplit(self, matrix):
        #Splits the training set into a training set and a testing set in the form of a numpy array.
        test = np.zeros(matrix.shape)
        train = matrix.copy()

        for user in np.arange(matrix.shape[0]):
            testRatings = np.random.choice(matrix[user, :].nonzero()[0],size=15,replace=True)
            train[user, testRatings] = 0
            test[user, testRatings] = matrix[user, testRatings]

        return train, test

    def RMSE(self, real, predicted):
        #Returns the root mean squared error between a given real and predicted value.
        return np.sqrt(((real - predicted)**2).mean())

    def predictions(self, U, I, Bi, Bu):
        #Generates a prediction for the rating based off of learned values.
        product = np.dot(U.T, I)
        predRating = 3.6 + Bi + Bu + product
        return predRating

    def trainModel(self, matrix) -> None:
        #Trains the model using Stochastic Gradient Descent.

        self.train, self.test = self.trainTestSplit(matrix)

        self.userMatrix = 3 * np.random.rand(self.latentDims, self.train.shape[0])
        self.itemMatrix = 3 * np.random.rand(self.latentDims, self.train.shape[1])
        self.userBias = 0
        self.itemBias = 0

        intRatings = self.train.nonzero()
        self.mu = np.average(intRatings)


        users, items = self.train.nonzero()

        for epoch in range(self.epochs):
            for u, i in zip(users, items):
                error = self.train[u, i] - self.predictions(self.userMatrix[:,u], self.itemMatrix[:,i], self.itemBias, self.userBias)
                self.userBias = self.userBias + self.trainingRate * (error - (self.lmb*self.userBias))
                self.itemBias = self.itemBias + self.trainingRate * (error - (self.lmb*self.itemBias))
                self.userMatrix[:, u] = self.userMatrix[:,u] + self.trainingRate * (error * self.itemMatrix[:, i] - self.lmb*self.userMatrix[:, u])
                self.itemMatrix[:, i] = self.userMatrix[:,u] + self.trainingRate * (error * self.userMatrix[:, u] - self.lmb*self.itemMatrix[:, i])
            

        return self

    def predict(self):
        #Creates a list of predictions for a given user.
        predicted = self.predictions(self.userMatrix, self.itemMatrix, self.itemBias, self.userBias)
        predictedIndex = np.where(self.train[self.userIndex, :] == 0)[0]
        return predicted[self.userIndex, predictedIndex]

    def createMovieRatings(self, moviesDF, moviesIndex, ratings, n= 10):
        #returns top 10 movies based on predicted ratings.
        movieIds = self.database.columns[moviesIndex]
        movieRatings = pd.DataFrame(data=dict(movieId = movieIds, rating = ratings))
        topMovies = movieRatings.sort_values("rating", ascending = False).head(n)
        
        return topMovies

    def generateRecommendation(self):
        #Main sequence: handles preprocessing, training, and displaying the top 10 recommendations.
        mat = self.preprocessing()
        self.trainModel(mat)

        self.userIndex = self.database.index.get_loc(self.UID)
        predictionsIndex = np.where(self.train[self.userIndex, :] == 0)[0]

        self.predictedRatings = self.predict()

        rec = self.createMovieRatings(self.movies, predictionsIndex, self.predictedRatings)
        rec.set_index('movieId', inplace = True)
        predictedMovieIds = rec.index.to_numpy().astype(int)

        moviesIndex = rec.index.to_numpy()

        movieNames = self.movies[self.movies['movieId'].isin(moviesIndex.astype(int))]


        return predictedMovieIds

class CBF:
    def __init__(self, user, train, test,  eval, newUser):
        #Intialises variables to be used throughout class.
        self.eval = eval
        if self.eval == True:
            self.train = train
            self.test = test
        elif self.eval == False:
            self.dataset = pd.read_csv('./cleaned_data.csv')
            self.train, self.test = train_test_split(self.dataset, test_size=0.33)
        
        self.movies = pd.read_csv('./ml-latest-small/movies.csv')
        self.genres_matrix = pd.read_csv('./genres_matrix.csv')
        self.currentUserId = user
        self.newUser = newUser



    def createUserProfile(self):
        #Creates a user profile based on the results of the collaborative filtering model
        #in combination with previosuly rated movies.
        CF = RS(self.currentUserId)

        if self.newUser == True and self.eval == False:
            self.currentUserId = CF.newUser()
        elif self.newUser == False and self.eval == False:
            self.currentUserId = CF.currentUser()

        CFResults = CF.generateRecommendation()
        ratedDF = self.train[self.train['userId'].isin([self.currentUserId])]
        ratedDF = ratedDF.append(self.train[self.train['movieId'].isin(CFResults)].drop_duplicates(subset='movieId', keep="last"))
        ratedDF.set_index('movieId', inplace = True)

        ratedMovies = self.movies[self.movies.index.isin(ratedDF.index)]
        ratedGenresMatrix = self.genres_matrix[self.genres_matrix.index.isin(ratedDF.index)]

        self.userAverageRating = round(ratedDF['rating'].mean(),1)

        userProfile = pd.DataFrame(columns=self.genres_matrix.columns)
        userProfile.append(pd.Series(name=self.currentUserId))
        for column in userProfile:
            selectedMovies = ratedGenresMatrix.loc[ratedGenresMatrix[column] == 1]
            selectedMovieRatings = ratedDF[ratedDF.index.isin(selectedMovies.index)]
            selectedMovieRatings.loc[:,'rating'] = selectedMovieRatings['rating'].apply(lambda x: x - self.userAverageRating)
            ratingsMean = selectedMovieRatings['rating'].mean()
            userProfile.loc[self.currentUserId, column] = ratingsMean
        
        userProfile.fillna(0, inplace = True)

        return userProfile

    def generatePrediciton(self):
        #Generates top predicitons for the active user.
        userProfile = self.createUserProfile()
        self.similarityMatrix = pd.DataFrame(columns = ['movieId', 'Title', 'Similarity'])
        for id in self.genres_matrix.index:
            currentRow = self.genres_matrix.loc[id]
            similarity = 1 - spatial.distance.cosine(userProfile.to_numpy().reshape(-1,1), currentRow.to_numpy().reshape(-1,1))
            self.similarityMatrix.append(pd.Series(name=id))
            self.similarityMatrix.loc[id, 'movieId'] = id
            self.similarityMatrix.loc[id, 'Title'] = id #self.movies.loc[self.movies['movieId'] == id, 'title']
            self.similarityMatrix.loc[id, 'Similarity'] = similarity
        

        self.similarityMatrix = self.similarityMatrix.sort_values(by=['Similarity'], ascending = False).dropna()
        top10Recommended = self.similarityMatrix['movieId'].head(10).to_numpy()
        top10Recommended = self.movies[self.movies['movieId'].isin(top10Recommended)].drop(labels=['genres','movieId'], axis = 1)

        print("Top Recommended Movies For You! ")
        print(top10Recommended)

        if self.eval == True:
            f1, div, TP, FP, TN, FN = self.evaluate()
            return f1, div, TP, FP, TN, FN


    def evaluate(self):
        #Calculates divserity and f1-score of the model.
        totalSimilarity = 0
        totalComparisons = 0

        recommendedIds = self.similarityMatrix['movieId'].head(10).to_numpy()

        for i in range(0, len(recommendedIds)):
            profile1 = self.genres_matrix[self.genres_matrix.index == recommendedIds[i]]
            for j in range(i, len(recommendedIds)):
                profile2 = self.genres_matrix[self.genres_matrix.index == recommendedIds[j]]
                totalSimilarity += spatial.distance.cosine(profile1.to_numpy().reshape(-1,1), profile2.to_numpy().reshape(-1,1))
                totalComparisons += 1

        
        recommendationDiversity = 1 - (totalSimilarity/totalComparisons)

        testUser = self.test['userId'].value_counts().max()
        currentUserTest = self.test[self.test['userId'] == self.currentUserId]

        currentUserTest['rating'] = [1 if r > 3.5 else 0 for r in currentUserTest['rating']]
        self.similarityMatrix['Similarity'] = [1 if s > 0 else 0 for s in self.similarityMatrix['Similarity']]

        TP = 0
        FP = 0
        TN = 0
        FN = 0
        TOTAL = 0

        for id, rating in zip(currentUserTest['movieId'], currentUserTest['rating']):

            try:
                predictedRating = self.similarityMatrix.loc[self.similarityMatrix['movieId'] == id, 'Similarity'].iloc[0]
            
                if predictedRating == 1 and rating == 1:
                    TP +=1
                elif predictedRating == 1 and rating == 0:
                    FP += 1
                elif predictedRating == 0 and rating == 0:
                    TN +=1
                else:
                    FN +=1
                TOTAL +=1 
            except:
                pass
            

            

        if TP + FP != 0:
            precision = TP/(TP+FP)
        else:
            precision = 0

        if TP + FN != 0:
            recall = TP/(TP+FN)
        else:
            recall = 0

        try:

            f1Score = 2*((precision*recall)/(precision + recall))

        except:
            f1Score = 0
            pass

        
        #print(f1Score, recommendationDiversity)
        return f1Score, recommendationDiversity, TP, FP, TN, FN


def evaluateModel():
        dataset = pd.read_csv('./cleaned_data.csv')
        train, test = train_test_split(dataset, test_size=0.33)
        test = test.reset_index()
        
        uniqueUsers = test['userId'].unique()
        uniqueUsers = test.index[test['userId'].isin(uniqueUsers)]

        f1ScoreList = []
        diversityList = []
        totalTP = 0
        totalFP = 0
        totalTN = 0
        totalFN = 0
        for user in uniqueUsers[:20]:
            userInstance = CBF(user, train, test, True, False)
            values = userInstance.generatePrediciton()
            f1ScoreList.append(values[0])
            diversityList.append(values[1])
            totalTP += values[2]
            totalFP += values[3]
            totalTN += values[4]
            totalFN += values[5]
        
        print("f1 scores : ", f1ScoreList)
        print("Diversity list: ", diversityList)
        print("TOTAL TP = ", totalTP)
        print("TOTAL FP = ", totalFP)
        print("TOTAL TN = ", totalTN)
        print("TOTAL FN = ", totalFN)

        print("Average f1 score = ", statistics.mean(f1ScoreList))
        print("Average Divserity = ", statistics.mean(diversityList))

def main():


    print("[0]  New User")
    print("[1]  Current User")
    print("[2]  Evaluate")
    print("[3]  Info")

    userStatus = input("Please select whether you are a new or current user: ")

    if userStatus == "0":
        rec = CBF(30, 0, 0, False, True)
        rec.generatePrediciton()
    elif userStatus == "1":
        rec = CBF(30, 0, 0, False, False)
        rec.generatePrediciton()
    elif userStatus == "2":   
        evaluateModel()
    elif userStatus == "3":
        print("This is a Recommender System Based on Collaborative filtering. \n")
        print("Selecting New User will prompt you to enter 5 movies that you have previously seen and give them a rating. This allows the system to build a profile for you so it can give accurate recommendations. \n")
        print("Selecting Current User will give you the option to select from 3 current users and get movie recommendations based on their preferences. \n")
        print("Selecting evaluate will return the f1-score and diversity score for the model to evaluate its efficacy")
    else:
        print("Please enter a valid input")


if __name__ == "__main__":
    main()



    

